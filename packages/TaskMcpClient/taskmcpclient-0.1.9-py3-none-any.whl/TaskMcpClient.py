# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250428-104133
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
启动MCP客户端，连带MCP服务端
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrettyPrintStr, PrintAndSleep
import os
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# from FuncForSettings import GetCurrentWorkParam
from LoadMcpServerConfig import LoadMcpServerConfig
from LlmServer import LlmServer
from FileQueryResult import FileQueryResult


class TaskMcpClient:
    SEP_CHAR_NAME = '.'  # MCP Server 服务名与函数名的分隔符

    def __init__(self):
        self.sWorkDir = os.getcwd()
        PrintTimeMsg(f'TaskMcpClient.sWorkDir={self.sWorkDir}=')
        self.exit_stack = AsyncExitStack()

        oLoadConfig = LoadMcpServerConfig(self.sWorkDir)
        # self.dictCmdPath = GetCurrentWorkParam('dictCmdPath')
        # self.dictMcpServers = GetCurrentWorkParam('dictMcpServers')
        self.dictCmdPath = oLoadConfig.dictCmdPath
        self.dictMcpServers = oLoadConfig.dictMcpServers

        self.dictSessionByName = {}  # 通过 服务名 映射 Sessioon
        self.lsServFuncTools = []  # MCP Server 服务端工具列表
        self.oLlm = LlmServer(self.sWorkDir)
        self.oTask = FileQueryResult(self.sWorkDir)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def _register_one_mcp_server(self, sName, dictMcpServer):
        """注册一个MCP服务"""
        sType = dictMcpServer.get('type', '')
        if sType not in ['stdio', 'sse']:
            PrintTimeMsg('_register_one_mcp_server({sName}).type={sType}=Error,SKIP!')
            return
        if sType == 'stdio':
            sCmd = dictMcpServer.get('cmd', '')
            if not sCmd:
                sCmd = dictMcpServer.get('command', '')
            server_params = StdioServerParameters(
                command=self.dictCmdPath.get(sCmd, sCmd),
                args=dictMcpServer.get('args', []),
                env=dictMcpServer.get('env', None),
            )
            PrintTimeMsg(f'_register_one_mcp_server({sName}).server_params={server_params}=')
            rwContext = await self.exit_stack.enter_async_context(stdio_client(server_params))
            # read_stream, write_stream = rwContext
            # oSession = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            # await oSession.initialize()
            # PrintTimeMsg(f'_register_one_mcp_server({sName}).oSession.initialize!')
            # self.dictSessionByName[sName] = oSession
            # async with stdio_client(server_params) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByName[sName] = oSession
        else:
            sUrl = dictMcpServer.get('url', '')
            dictHeader = dictMcpServer.get('headers', {})
            PrintTimeMsg(f'_register_one_mcp_server({sName}).sUrl={sUrl},dictHeader={dictHeader}=')
            # 如下写法，oSession 被释放了
            # async with sse_client(sUrl, dictHeader) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByName[sName] = oSession
            rwContext = await self.exit_stack.enter_async_context(sse_client(sUrl, dictHeader))
        read_stream, write_stream = rwContext
        oSession = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await oSession.initialize()
        PrintTimeMsg(f'_register_one_mcp_server({sName}).oSession.initialize!')
        self.dictSessionByName[sName] = oSession

    async def _list_prompts(self):
        # 获取所有 Prompt 模板, WeiYF.测试内容为空
        lsPrompts = []
        for sName, oSession in self.dictSessionByName.items():
            response = await oSession.list_prompts()
            PrintTimeMsg(f'_list_prompts({sName})={PrettyPrintStr(response)}=')
            lsPrompts.append([prompt.name for prompt in response.prompts])
        PrintTimeMsg(f'_list_prompts()={PrettyPrintStr(lsPrompts)}=')

    async def _gather_available_tools(self):
        """汇总所有MCP服务的工具列表"""
        self.lsServFuncTools = []
        for sName, oSession in self.dictSessionByName.items():
            response = await oSession.list_tools()
            for tool in response.tools:
                self.lsServFuncTools.append({
                    "type": "function",  # OpenAI兼容写法
                    "function": {
                        "name": f"{sName}{self.SEP_CHAR_NAME}{tool.name}",
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                        # 'required': tool.required,  # no required
                    }
                })
        PrintTimeMsg(f"_gather_available_tools.len(self.lsServFuncTools)={len(self.lsServFuncTools)}=")

    async def connect_mcp_servers(self):
        """连接到多个MCP服务端"""
        for sName, dictMcpServer in self.dictMcpServers.items():
            if sName.startswith('@'):  # 跳过代码示例
                continue
            # PrintTimeMsg(f'connect_mcp_servers({sName})={PrettyPrintStr(dictMcpServer)}=')
            await self._register_one_mcp_server(sName, dictMcpServer)

        # PrintTimeMsg(f'connect_mcp_servers.dictSessionByName={self.dictSessionByName}=')
        PrintTimeMsg(f"connect_mcp_servers.len(self.dictSessionByName)={len(self.dictSessionByName)}=")
        await self._gather_available_tools()
        # await self._list_prompts()
        # PrintTimeMsg(f'connect_mcp_servers.lsServFuncTools={self.lsServFuncTools}=')
        return

    async def _callbackTool(self, sFullFuncName, lsArgs):
        PrintTimeMsg(f"_callbackTool(sName={sFullFuncName}, lsArgs={lsArgs})")
        sName, cSep, sFunc = sFullFuncName.partition(self.SEP_CHAR_NAME)
        oSession = self.dictSessionByName.get(sName, None)
        if oSession:
            return await oSession.call_tool(sFunc, lsArgs)
        sErrMsg = f'_callbackTool.sFullFuncName={sFullFuncName}=NotFound!'
        PrintTimeMsg(f'_callbackTool.sErrMsg={sErrMsg}=Warning!')
        # sys.exit(-404)
        return sErrMsg

    async def loop_mcp_chat(self):
        """MCP交互聊天循环"""
        PrintTimeMsg("loop_mcp_chat.MCP Client Started!")
        # PrintTimeMsg("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                # query = '洛杉矶的天气怎样？'
                # # query = '1234 + 7890 = ?'
                # query = 'xuanyuan的视频里面，网络安全主题相关的播放最高的是哪个?'
                # 调用LLM及工具
                final_text = await self.oLlm.process_query(query, self.lsServFuncTools, self._callbackTool)
                PrintTimeMsg(f"loop_mcp_chat.final_text={final_text}=")
                # break
            except Exception as e:
                PrintTimeMsg(f"loop_mcp_chat.e={repr(e)}=")

    async def loop_mcp_file_query(self):
        """MCP循环监听处理文件请求"""
        PrintTimeMsg("loop_mcp_file_query.MCP Client Started!")

        async def callbackQueryResult(sRequestText):
            PrintTimeMsg(f"callbackQueryResult.sRequestText={sRequestText}=")
            sResultText = await self.oLlm.process_query(sRequestText, self.lsServFuncTools, self._callbackTool)
            return sResultText

        iLoopCnt = 0
        while True:
            iSleepSeconds = 60
            try:
                lsNoExtFN = self.oTask.list_file_query_task()
                for sNoExtFN in lsNoExtFN:
                    await self.oTask.deal_file_query_result(sNoExtFN, callbackQueryResult)
            except Exception as e:
                PrintTimeMsg(f"loop_mcp_file_query.e={repr(e)}=")
            PrintAndSleep(iSleepSeconds, f'WaitForNext.iLoopCnt={iLoopCnt}')
            iLoopCnt += 1


async def mainTaskMcpClient():
    sRunMode = 'chat'  # 默认是聊天模式
    if len(sys.argv) >= 2:
        sRunMode = sys.argv[1]

    client = TaskMcpClient()
    try:
        await client.connect_mcp_servers()
        # PrintAndSleep(10, 'JustWait')
        if sRunMode == 'chat':
            await client.loop_mcp_chat()
        elif sRunMode == 'task':
            await client.loop_mcp_file_query()
        else:
            await client.loop_mcp_chat()
    finally:
        await client.cleanup()


def asyncio_loop_run(cbASyncFunc):
    # 循环等待执行异步IO函数
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cbASyncFunc())


def main():
    asyncio_loop_run(mainTaskMcpClient)


if __name__ == '__main__':
    main()
