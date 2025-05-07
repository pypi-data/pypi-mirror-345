from typing import Union
from jinja2 import Template
import logging
import re, io, os, sys, json, logging
import inspect
import base64
import traceback
from codyer import skills
import uuid

def general_llm_token_count(messages):
    # 统一token计算方式
    def count_str(string):
        # 字母/数字/符号/换行等 0.3 token, 其他 0.6 token
        normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \n"
        count = 0
        for c in string:
            if c in normal_chars:
                count += 0.3
            else:
                count += 0.6
        return count
    num_tokens = 0
    for message in messages:
        if isinstance(message["content"], str):
            num_tokens += count_str(message["content"])
        else:
            for item in message["content"]:
                if isinstance(item, str):
                    num_tokens += count_str(item)
                else:
                    if "text" in item:
                        num_tokens += count_str(item["text"])
                    elif "image" in item:
                        num_tokens += 1615
                    else:
                        raise Exception("message type wrong")
    return num_tokens

def temp_sonnet_llm_token_count(messages):
    def count_str(string):
        normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \n"
        
        def count_normal_text(text):
            count = 0
            for c in text:
                if c in normal_chars:
                    count += 0.25
                else:
                    count += 1.2
            return count
        
        # 检测是否包含代码块
        if "```" in string:
            code_multiplier = 1.4  # 代码块权重系数
            total_count = 0
            remaining_text = string
            
            # 查找并处理所有代码块
            while "```" in remaining_text:
                start_pos = remaining_text.find("```")
                # 处理代码块前的普通文本
                normal_text = remaining_text[:start_pos]
                if normal_text:
                    total_count += count_normal_text(normal_text)
                
                # 裁剪并查找代码块结束位置
                remaining_text = remaining_text[start_pos + 3:]
                end_pos = remaining_text.find("```")
                
                if end_pos == -1:  # 没有找到结束标记
                    # 剩余文本作为普通文本处理
                    total_count += count_normal_text(remaining_text)
                    break
                
                # 提取代码内容并计算(应用乘数)
                code_content = remaining_text[:end_pos]
                total_count += count_normal_text(code_content) * code_multiplier
                
                # 继续处理剩余文本
                remaining_text = remaining_text[end_pos + 3:]
            
            # 处理最后剩余的普通文本
            if remaining_text and "```" not in remaining_text:
                total_count += count_normal_text(remaining_text)
                
            return total_count
        else:
            # 不含代码块的普通文本
            return count_normal_text(string)
        
    num_tokens = 0
    for message in messages:
        if isinstance(message["content"], str):
            num_tokens += count_str(message["content"])
        else:
            for item in message["content"]:
                if isinstance(item, str):
                    num_tokens += count_str(item)
                else:
                    if "text" in item:
                        num_tokens += count_str(item["text"])
                    elif "image" in item:
                        num_tokens += 1615
                    else:
                        raise Exception("message type wrong")
    return num_tokens

def show_messages(messages):
    import logging
    logging.debug('-'*50 + '<LLM Messages>' + '-'*50)
    for message in messages:
        logging.debug(f'[[[ {message["role"]} ]]]')
        logging.debug(f'{message["content"]}')
    logging.debug('-'*50 + '</LLM Messages>' + '-'*50)

def openai_format_llm_inference(messages, stream=False, api_key=None, base_url=None, model=None, input_price=None, output_price=None, max_retries=2, timeout=20, max_tokens=8096):
    """
    OpenAI格式的LLM推理
    @messages: list, [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url'}]}]
    @stream: bool, 是否流式输出
    @api_key: str,  LLM api_key
    @base_url: str,  LLM base_url
    @model: str,  LLM model
    @input_price: float, 输入 token/1k 价格
    @output_price: float, 输出 token/1k 价格
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url, max_retries=max_retries, timeout=timeout)

    show_messages(messages)

    def _messages_to_openai(messages):
        # 消息格式转换成openai格式
        def encode_image(image_path):
            if image_path.startswith('http'):
                return image_path
            bin_data = base64.b64encode(open(image_path, "rb").read()).decode('utf-8')
            image_type = image_path.split('.')[-1].lower()
            return f"data:image/{image_type};base64,{bin_data}"
        new_messages = []
        for message in messages:
            content = message["content"]
            if isinstance(content, str):
                new_messages.append({"role": message["role"], "content": content})
            elif isinstance(content, list):
                new_content = []
                for c in content:
                    if isinstance(c, str):
                        new_content.append({"type": "text", "text": c})
                    elif isinstance(c, dict):
                        if "image" in c:
                            new_content.append({"type": "image_url", "image_url": {"url": encode_image(c["image"])}})
                        elif "text" in c:
                            new_content.append({"type": "text", "text": c["text"]})
                new_messages.append({"role": message["role"], "content": new_content})
        return new_messages

    openai_messages = _messages_to_openai(messages)

    def _with_stream():
        input_tokens = None
        output_tokens = None
        result = ''
        try:
            response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=True, stream_options={"include_usage": True})
            for chunk in response:
                if len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None and len(chunk.choices[0].delta.reasoning_content) > 0:
                        token = chunk.choices[0].delta.reasoning_content
                    else:
                        token = chunk.choices[0].delta.content
                    if token is None:
                        continue
                    yield token
                    if token is not None:
                        result += token
                if chunk.usage is not None:
                    input_tokens = chunk.usage.prompt_tokens
                    output_tokens = chunk.usage.completion_tokens
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM stream error')
            raise e
        finally:
            if input_price is not None and output_price is not None and len(result.strip()) > 0:
                if input_tokens is None:
                    input_tokens = general_llm_token_count(messages)
                    output_tokens = general_llm_token_count([{"role": "assistant", "content": result}])
                cost = input_price * input_tokens / 1000.0 + output_price * output_tokens / 1000.0
                logging.info(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
    
    def _without_stream():
        try:
            response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=False)
            if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content is not None and len(response.choices[0].message.reasoning_content) > 0:
                result = response.choices[0].message.reasoning_content  + '\n' + response.choices[0].message.content
            else:
                result = response.choices[0].message.content
            if input_price is not None and output_price is not None:
                input_tokens, output_tokens = response.usage.prompt_tokens, response.usage.completion_tokens
                cost = input_price * input_tokens / 1000.0 + output_price * output_tokens / 1000.0
                logging.info(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM error')
            raise e
    
    if stream:
        return _with_stream()
    else:
        return _without_stream()


def anthropic_format_llm_inference(messages, stream=False, client=None, api_key=None, base_url=None, model=None, input_price=None, output_price=None, max_tokens=8096):
    """
    Anthropic格式的LLM推理
    @messages: list, [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url'}]}]
    @stream: bool, 是否流式输出
    @api_key: str,  LLM api_key
    @base_url: str,  LLM base_url
    @model: str,  LLM model
    @input_price: float, 输入 token/1k 价格
    @output_price: float, 输出 token/1k 价格
    """
    from anthropic import Anthropic
    client = client or Anthropic(api_key=api_key, base_url=base_url, max_retries=3)

    show_messages(messages)

    def _messages_to_anthropic(messages):
        # 消息格式转换成anthropic格式
        def encode_image(image_path):
            bin_data = base64.b64encode(open(image_path, "rb").read()).decode('utf-8')
            image_type = image_path.split('.')[-1].lower()
            return { "type": "base64", "media_type": f"image/{image_type}", "data": bin_data}
        new_messages = []
        for message in messages:
            role = message["role"]
            role = 'assistant' if role == "system" else role
            content = message["content"]
            if isinstance(content, str):
                new_messages.append({"role": role, "content": content})
            elif isinstance(content, list):
                new_content = []
                for c in content:
                    if isinstance(c, str):
                        new_content.append({"type": "text", "text": c})
                    elif isinstance(c, dict):
                        if "image" in c:
                            new_content.append({"type": "image", "source": encode_image(c["image"])})
                        elif "text" in c:
                            new_content.append({"type": "text", "text": c["text"]})
                new_messages.append({"role": role, "content": new_content})
        return new_messages

    messages = _messages_to_anthropic(messages)

    def _with_stream():
        i_count = None
        o_count = None
        try:
            result = ''
            stream = client.messages.create(max_tokens=max_tokens, messages=messages, model=model, stream=True)
            for event in stream:
                if event.type == 'content_block_delta':
                    token = event.delta.text
                    if token is None:
                        continue
                    yield token
                    if token is not None:
                        result += token
                if event.type == 'message_start':
                    i_count = event.message.usage.input_tokens
                if event.type == 'message_delta':
                    o_count = event.usage.output_tokens
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM stream error')
            raise e
        finally:
            if input_price is not None and output_price is not None:
                if len(result.strip()) > 0:
                    if i_count is None:
                        # i_count = client.messages.count_tokens(model=model, messages=messages).input_tokens
                        i_count = temp_sonnet_llm_token_count(messages)
                    if o_count is None:
                        # o_count = client.messages.count_tokens(model=model, messages=[{"role": "assistant", "content": result}]).output_tokens
                        o_count = temp_sonnet_llm_token_count([{"role": "assistant", "content": result}])
                    cost = input_price * i_count / 1000.0 + output_price * o_count / 1000.0
                    logging.info(f"input_tokens: {i_count}, output_tokens: {o_count}, cost: {cost}")
                    skills.system.server.consume('llm_inference', cost)
    def _without_stream():
        try:
            response = client.messages.create(max_tokens=max_tokens, messages=messages, model=model, stream=False)
            if input_price is not None and output_price is not None:
                i_count, o_count= response.usage.input_tokens, response.usage.output_tokens
                cost = input_price * i_count / 1000.0 + output_price * o_count / 1000.0
                logging.info(f"input_tokens: {i_count}, output_tokens: {o_count}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
            result = response.content[0].text
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM error')
            raise e
    
    if stream:
        return _with_stream()
    else:
        return _without_stream()

def default_stream_output(token):
    if token is not None:
        print(token, end="", flush=True)
    else:
        print("\n", end="", flush=True)


def get_function_signature(func, module: str = None):
    """Returns a description string of function"""
    func_type = type(func).__name__
    try:
        if func_type == "function":
            sig = inspect.signature(func)
            sig_str = str(sig)
            desc = f"{func.__name__}{sig_str}"
            if func.__doc__:
                desc += ": " + func.__doc__.strip()
            if module is not None:
                desc = f"{module}.{desc}"
            if inspect.iscoroutinefunction(func):
                desc = "" + desc
        else:
            method_name = ".".join(func.chain)
            signature = skills.system.server.get_function_signature(method_name) + '\nimport by: `from codyer import skills`\n'
            return signature
        return desc
    except Exception as e:
        logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
        return ""


class TmpManager:
    def __init__(self, agent):
        self.agent = agent
        self.tmp_index = None # 临时消息的起始位置

    def __enter__(self):
        self.tmp_index = len(self.agent.messages)
        return self.agent

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.agent.messages = self.agent.messages[:self.tmp_index] 
        self.tmp_index = None
        if exc_type:
            self.agent.handle_exception(exc_type, exc_val, exc_tb)
        return False

defalut_python_prompt_template = """
# 运行python代码

- 有必要才运行python代码
- 有结果直接输出结论，不再运行python
- 不要重复执行相同的代码

## 运行格式

```python
# run code
xxx
```

## Available imported functions
```
{{python_funcs}}
```

"""

class Agent:
    python_prompt_template = defalut_python_prompt_template

    def __init__(self, 
            role: str = "You are a helpfull assistant.",
            functions: list = [],
            workspace: str = None,
            stream_output=default_stream_output,
            model=None,
            llm_inference=skills.codyer.llm.llm_inference,
            llm_token_count=general_llm_token_count,
            llm_token_limit=64000,
            continue_run=False,
            messages=None,
            enable_python=True,
            max_react=5, # 最大re act次数
            interpretors = [], # 解析器 [is_match, parse, 'realtime' or 'final']
        ):
        """
        @role: str, agent role description
        @functions: list, can be used by the agent to run python code
        @workspace: str, agent保存记忆的工作空间，默认值为None（不序列化）。如果指定了目录，Agent会自动保存状态并在下次初始化时重新加载。
        @stream_output: function, agent输出回调函数
        @llm_inference: function, LLM推理函数
        @llm_token_limit: int, LLM token limit, default 64000
        @continue_run: bool, 是否自动继续执行。Agent在任务没有完成时，是否自动执行。默认为True.
        @messages: list, agent记忆 [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url | image_path']}]
        @enable_python: bool, 是否启用agent执行python代码和调用functions
        @max_react: int, 最大re act次数
        @interpretors: list, 解析器 [(is_match, parse, realtime|final), ...]. is_match(llm_output) -> bool, parse(llm_output) -> (result, log)
            parse: return (python_mode, python_result, result)
        """
        if workspace is not None and not os.path.exists(workspace):
            os.makedirs(workspace)
        self.role = role
        self.workspace = workspace
        if self.workspace is None:
            self.python_pickle_path = uuid.uuid4().hex + '.pickle'
        else:
            self.python_pickle_path = os.path.join(workspace, 'python.pickle')
        self.functions = functions
        # llm_inference 必须是数组 或者 函数
        self.model = model
        if self.model is None:
            if not callable(llm_inference) and not isinstance(llm_inference, list):
                raise ValueError("llm_inference must be a function or a list of functions")
            if callable(llm_inference):
                self.llm_inferences = [llm_inference]
            else:
                self.llm_inferences = llm_inference
        else:
            self.llm_inferences = [skills.codyer.llm.llm_inference]
        self.llm_token_count = llm_token_count
        self.llm_token_limit = llm_token_limit
        self.continue_run = continue_run
        self.stream_output = stream_output
        self.messages = messages or self.load_messages()
        self._enable_python = enable_python
        self._max_react = max_react
        for item in interpretors:
            if len(item) == 2:
                is_match, to_parse = item
                mode = 'final'
            else:
                is_match, to_parse, mode = item
            if not callable(is_match) or not callable(to_parse) or mode not in ['realtime', 'final']:
                raise ValueError("interpretors must be a list of (is_match, parse, 'realtime' or 'final')")
        self._interpretors = interpretors
        self.llm_run_count = 0

    def add_message(self, role, content):
        if isinstance(content, list):
            content = [x.strip() if isinstance(x, str) else x for x in content]
        else:
            content = content.strip() if isinstance(content, str) else content
        if len(self.messages) > 0 and self.messages[-1]["role"] == role:
            if isinstance(self.messages[-1]["content"], str) and isinstance(content, str):
                self.messages[-1]["content"] += '\n\n' + content
            else:
                self.messages.append({"role": role, "content": content})
        else:
            self.messages.append({"role": role, "content": content})
        self.save_messages()

    def load_messages(self):
        if self.message_path is not None and os.path.exists(self.message_path):
            with open(self.message_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
        
    def get_history(self):
        """
        获取历史消息
        @return: list, [{"role": "assistant|user", "content": "content"}, ...]
        """
        messages = []
        for message in self.messages:
            if message["role"] in ['system', 'assistant']:
                role = 'assistant'
            else:
                role = 'user'
            content = message["content"]
            if isinstance(content, list):
                new_content = ''
                for c in content:
                    if isinstance(c, str):
                        new_content += c + '\n'
                    elif isinstance(c, dict):
                        if 'image' in c:
                            new_content += f'![{c["image"]}]({c["image"]})\n'
                        else:
                            new_content += c['text'] + '\n'
                content = new_content
            messages.append({"role": role, "content": content})
        return messages

    def save_messages(self):
        if self.workspace is None:
            return
        with open(self.message_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False)

    @property
    def message_path(self):
        return os.path.join(self.workspace, "memory.json") if self.workspace is not None else None

    def clear(self):
        """
        清楚agent状态
        """
        if self.message_path is not None and os.path.exists(self.message_path):
            os.remove(self.message_path)
        self.clear_python()
        self.messages = []

    def tmp(self):
        """
        agent临时状态，在with语句中执行的操作不会进入记忆
        用法:
        with agent.tmp() as agent:
            agent.user_input("hello")
        """
        return TmpManager(self)

    def disable_stream_output(self):
        """禁用输出回调函数"""
        self.tmp_stream_output = self.stream_output
        self.stream_output = default_stream_output

    def enable_stream_output(self):
        """启用输出回调函数"""
        self.stream_output = self.tmp_stream_output
        self.tmp_stream_output = default_stream_output

    def disable_python(self):
        self._enable_python = False

    def enable_python(self):
        self._enable_python = True

    def clear_python(self):
        if self.workspace is None:
            # 检测 self.python_pickle_path 文件是否存在，如果存在则删除
            if os.path.exists(self.python_pickle_path):
                os.remove(self.python_pickle_path)

    def run(self, command: Union[str, list], return_type=None, display=False):
        """
        执行命令并返回指定类型的结果
        @command: 命令内容, 格式为: str | ['text', {'image': 'image_url | image_path']}, ...]
        @return_type: type, 返回python类型数据，比如str, int, list, dict等
        @display: bool, 是否显示LLM生成的中间内容，当display为True时，通过stream_output输出中间内容
        """
        if not display:
            self.disable_stream_output()
        try:
            result = self._run(command, is_run_mode=True, return_type=return_type)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # return str(e)
            raise e
        finally:
            self.clear_python()
            if not display:
                self.enable_stream_output()

    def user_input(self, input: Union[str, list]):
        """
        agent响应用户输入，并始终通过stream_output显示LLM生成的中间内容
        input: 用户输入内容 str | ['text', {'image': 'image_url | image_path']}, ...]
        """
        try:
            result = self._run(input)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # return str(e)
            raise e
        finally:
            self.clear_python()
        # if self.continue_run:
        #     # 判断是否继续执行
        #     messages = self.messages
        #     messages = self._cut_messages(messages[-5:], 2*1000) # 最近5条消息 & < 2*1000 tokens
        #     the_prompt = "对于当前状态，如果无需用户输入或者确认，可以继续执行任务，请回复yes；其他情况回复no。"
        #     messages += [{"role": "assistant", "content": the_prompt}]
        #     for index, llm_inference in enumerate(self.llm_inferences):
        #         try:
        #             response = llm_inference(messages, stream=False)
        #             if "yes" in response.lower():
        #                 result = self.run("ok")
        #             break
        #         except Exception as e:
        #             if index < (len(self.llm_inferences) - 1):
        #                 continue
        #             else:
        #                 raise e
        # return result

    def _run(self, input, is_run_mode=False, return_type=None):
        # 如果是run模式 & 需要返回值类型
        if is_run_mode and return_type is not None:
            add_content = "\nYou should return python values in type " + str(return_type) + " by run python code(```python\n# run code\nxxx\n).\n"
            if isinstance(input, list):
                input = (input + [add_content])
            elif isinstance(input, str):
                input = input + add_content
            else:
                raise Exception("input type error")

        # 记录message
        self.add_message("user", input)

        # 记录llm请求次数
        self.llm_run_count = 0

        # 循环运行
        # while True:
        for _ in range(self._max_react):
            messages = self._get_llm_messages()
            llm_result, (python_mode, python_data, result, continue_run) = self._llm_and_parse_output(messages)
            # 次数+1
            self.llm_run_count += 1

            if is_run_mode and python_mode:
                return python_data
            
            if continue_run:
                message = f'**python运行结果**\n```output\n{python_data}\n```' if python_data is not None else f'**执行结果/日志**\n```output\n{result}\n```'
                self.add_message("user", message)
                # self.add_message("user", message)
                # self.stream_output(message)
                self.stream_output(None)
                self.stream_output("**继续执行**\n")
                continue
            else:
                return llm_result

    def _cut_messages(self, messages, llm_token_limit):
        while self.llm_token_count(messages) > llm_token_limit:
            messages.pop(0)
        return messages

    def _get_llm_messages(self):
        # 获取记忆 + prompt
        messages = self.messages
        if not self._enable_python:
            system_prompt = self.role
        else:
            funtion_signatures = "\n\n".join([get_function_signature(x) for x in self.functions])
            variables = {"python_funcs": funtion_signatures}
            python_prompt = Template(self.python_prompt_template).render(**variables)
            system_prompt = self.role + '\n\n' + python_prompt
        # 动态调整记忆长度
        system_prompt_count = self.llm_token_count([{"role": "system", "content": system_prompt}])
        left_count = int(self.llm_token_limit * 0.8) - system_prompt_count
        messages = self._cut_messages(messages, left_count)
        # 合并messages中，同类型的连续消息
        new_messages = []
        for message in messages:
            if len(new_messages) == 0 or new_messages[-1]["role"] != message["role"]:
                new_messages.append(message)
            else:
                if isinstance(new_messages[-1]["content"], str) and isinstance(message["content"], str):
                    new_messages[-1]["content"] += '\n\n' + message["content"]
                else:
                    new_messages.append(message)
        self.messages = new_messages
        self.save_messages()
        # 组合messages
        messages = [{"role": "system", "content": system_prompt}] + self.messages
        return messages
    
    def _run_python_match(self, result):
        # 检测是否有python代码需要运行
        parse = re.compile( "```python\n# run code\n(.*?)\n```", re.DOTALL).search(result)
        if parse is not None:
            # 将找到的内容后面的截断
            return True, result[:parse.end()]
        else:
            return False, result
        
    def _run_python(self, llm_result):
        """运行python代码，返回: (python_mode, python_data, result, continue)"""
        parse = re.compile( "```python\n# run code\n(.*?)\n```", re.DOTALL).search(llm_result)
        if parse is not None:
            code = parse.group(1)
            python_data, log = self._run_code(code)
            return True, python_data, log, True
        else:
            return False, None, '没有python代码执行', False

    def _llm_and_parse_output(self, messages):
        """return (llm_result, (python_mode, python_data, result, continue))"""
        llm_result = ""
        realtime_parse = None
        interpretors = self._interpretors
        if self._enable_python:
            interpretors = interpretors + [(self._run_python_match, self._run_python, 'realtime')]

        for index, llm_inference in enumerate(self.llm_inferences):
            try:
                if self.model is None:
                    response = llm_inference(messages, stream=True)
                else:
                    response = llm_inference(messages, stream=True, model=self.model)
                is_break = False
                for token in response:
                    # print(f'<<{token}>>')
                    llm_result += token
                    self.stream_output(token)
                    for test_match, parse, mode in interpretors:
                        if mode == 'realtime': # 如果是实时解析器，则解析
                            # 实时解析器必须返回是否匹配和新的llm_result(让送入messages的内容更加准确)
                            result = test_match(llm_result)
                            if isinstance(result, tuple):
                                is_match, new_llm_result = result
                            else:
                                is_match = result
                                new_llm_result = llm_result
                            if is_match:
                                llm_result = new_llm_result
                                realtime_parse = parse
                                is_break = True
                                break
                    if is_break:
                        break
                # 可能返回空的情况
                if len(llm_result) > 0:
                    break
                else:
                    self.stream_output('LLM返回空，进行重试')
                    continue
            except Exception as e:
                if index < (len(self.llm_inferences) - 1):
                    self.stream_output(f'LLM请求错误，进行重试')
                    self.stream_output(None)
                    logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
                    llm_result = ''
                    continue
                else:
                    raise e
        self.stream_output(None)
        # print(llm_result)
        if len(llm_result.strip()) > 0:
            self.add_message("assistant", llm_result)
        # 有实时解析器
        if realtime_parse is not None:
            parse_result = realtime_parse(llm_result)
            return llm_result, parse_result
        else:
            # 没有实时解析器
            parse_results = []
            for is_match, parse, mode in interpretors:
                if mode == 'final':
                    if is_match(llm_result):
                        parse_result = parse(llm_result)
                        parse_results.append(parse_result)
            if len(parse_results) > 0:
                python_mode = False
                python_result = None
                continue_run = False
                result = ''
                for _python_mode, _python_data, _result, _continue_run in parse_results:
                    if _python_mode:
                        python_mode = True
                        python_result = _python_data
                    if _continue_run:
                        continue_run = True
                    result += _result
                return llm_result, (python_mode, python_result, result, continue_run)
            else:
                return llm_result, (False, None, '', False)

    def _run_code(self, code):
        # 运行的代码里面不能有其他skills库
        default_import = """from codyer import skills\n"""
        code = default_import + code
        functions = [f for f in self.functions if type(f).__name__ == "function"] # 过滤掉skills相关函数
        python_result, log = skills._exec(self.python_pickle_path, code, functions=functions, names=[f.__name__ for f in functions])
        return python_result, log