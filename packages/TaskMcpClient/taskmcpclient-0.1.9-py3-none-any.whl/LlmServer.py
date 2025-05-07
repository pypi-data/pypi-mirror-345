# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250427-105337
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装MCP场景下的LLM服务
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
from openai import OpenAI
import os
import json
from dotenv import load_dotenv


class LlmServer:
    def __init__(self, sWorkDir=''):
        # PrintTimeMsg('LlmServer.__init__')
        sEnvFN = None
        if sWorkDir:
            sEnvFN = os.path.join(sWorkDir, '.env')
            PrintTimeMsg(f'LlmServer.sEnvFN={sEnvFN}=')
            self._check_init_env_file(sEnvFN)
        bLoad = load_dotenv(dotenv_path=sEnvFN, verbose=True)  # load environment variables from .env
        PrintTimeMsg(f"LlmServer.load_dotenv()={bLoad}")
        sOpenAiUrl = os.getenv("OPENAI_BASE_URL")
        sOpenAiKey = os.getenv("OPENAI_API_KEY")
        self.sOpenAiModel = os.getenv("OPENAI_MODEL")
        PrintTimeMsg(f'LlmServer.sOpenAiUrl={sOpenAiUrl}, sOpenAiModel={self.sOpenAiModel}')
        self.openai = OpenAI(api_key=sOpenAiKey, base_url=sOpenAiUrl)  # 兼容 OpenAI 客户端

    def _check_init_env_file(self, sEnvFN):
        # 创建 .env 并写入初始值
        if not os.path.exists(sEnvFN):
            lsEnvKey = [
                'OPENAI_BASE_URL',
                'OPENAI_API_KEY',
                'OPENAI_MODEL',
            ]
            with open(sEnvFN, 'w', encoding='utf-8') as f:
                for sK in lsEnvKey:
                    f.write(f'{sK}=\n')

    def get_response(self, lsMsg: list, lsTools: list):
        # 向 LLM 发起query请求
        response = self.openai.chat.completions.create(
            model=self.sOpenAiModel,
            # max_tokens=1000,
            messages=lsMsg,
            tools=lsTools,
        )
        PrintTimeMsg(f'get_response().response={response}')
        return response

    async def process_query(self, sQuery: str, lsTools: list, callbackTool) -> str:
        # 使用 OpenAI 和可用工具处理查询
        # callbackTool: Callable[[str, list], str]
        # WeiYF 严格声明函数原型，会增加python代码的复杂性，在应用开发中不提倡

        # 创建消息列表
        lsMsg = [{ "role": "user", "content": sQuery}]

        # available_tools = await self.get_tools()  # 列出可用工具
        response = self.get_response(lsMsg, lsTools)  # 处理消息

        # tool_results = []
        final_text = []  # 返回结果文本
        for choice in response.choices:
            message = choice.message
            if not message.tool_calls:  # 如果不调用工具，则添加到 final_text 中
                final_text.append(message.content)
            else:  # 如果是工具调用，则获取工具名称和输入
                # 解包tool_calls
                tool_name = message.tool_calls[0].function.name
                tool_args = json.loads(message.tool_calls[0].function.arguments)
                PrintTimeMsg(f"准备调用工具:【{tool_name}】参数:【{json.dumps(tool_args, ensure_ascii=False, indent=2)}】")
                # 执行工具调用，获取结果
                result = await callbackTool(tool_name, tool_args)
                # tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[调用工具:【{tool_name}】参数:【{tool_args}】, 返回【{result}】]")

                # 继续与工具结果进行对话
                if message.content and hasattr(message.content, 'text'):
                    lsMsg.append({
                      "role": "assistant",
                      "content": message.content
                    })
                # 将工具调用结果添加到消息
                lsMsg.append({
                    "role": "user",
                    "content": result.content
                })
                # 获取下一个LLM响应
                response = self.get_response(lsMsg, lsTools)
                # 将结果添加到 final_text
                final_text.append(response.choices[0].message.content)
        # PrintTimeMsg(f'process_query().tool_results={tool_results}')
        return "\\n".join(final_text)


def mainLlmServer():
    import asyncio
    o = LlmServer()
    # lsMessages = [{
    #     'role': 'user',
    #     'content': '天为什么蓝色的？'
    # }]
    # o.get_response(lsMessages, [])

    def callbackTool(sName, lsArgs):
        PrintTimeMsg(f"callbackTool(sName={sName}, lsArgs={lsArgs})")
        return f"callbackTool(sName={sName}, lsArgs={lsArgs})"

    asyncio.run(o.process_query('天为什么蓝色的？', [], callbackTool))


if __name__ == '__main__':
    mainLlmServer()
