import logging
import asyncio

from meshagent.api import RoomMessage
from meshagent.api.room_server_client import RoomClient

from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, silero
#from livekit.plugins.turn_detector.multilingual import MultilingualModel
import uuid
import asyncio
import logging


from livekit.plugins import openai

from livekit.plugins import openai, silero
from livekit import rtc
from livekit.agents import Agent, AgentSession

from typing import Optional

from copy import deepcopy

from meshagent.api.schema_util import merge, prompt_schema

from meshagent.agents import SingleRoomAgent


logger = logging.getLogger("voice")


from meshagent.agents.agent import AgentCallContext


class VoiceConnection:
    def __init__(self, *, room: RoomClient, breakout_room: str):
        self.room = room
        self.breakout_room = breakout_room
     
    async def __aenter__(self):

        client = self.room
    
        room_options = rtc.RoomOptions(auto_subscribe=True)

        room = rtc.Room()

        self.livekit_room = room

        connection_info = await client.livekit.get_connection_info(breakout_room=self.breakout_room)
        
        await room.connect(url=connection_info.url, token=connection_info.token, options=room_options)

        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.livekit_room.disconnect()

class Voicebot(SingleRoomAgent):

    def __init__(
        self,
        name: str,
        input_schema: Optional[dict] = None, # the base schema, voice agent parameters will be added
        title: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[list[str]] = None,
        rules: Optional[list[str]] = None,
        auto_greet_prompt: Optional[str] = None,
        greeting: Optional[str] = None,
    ):
        if rules == None:
            rules = [ "You are a helpful assistant communicating through voice." ]
        
        self.auto_greet_prompt = auto_greet_prompt
        self.greeting = greeting

        self.rules = rules

        if input_schema == None:
            input_schema = None

        input_schema = merge(
            schema=input_schema,
            additional_properties={
        })
        
        super().__init__(
            name=name,
            description=description,
            title=title,
            labels=labels
        )

    async def start(self, *, room):
        await super().start(room=room)
        await room.local_participant.set_attribute("supports_voice", True)
        await room.messaging.enable()
        room.messaging.on("message", self.on_message)
    
    def on_message(self, message: RoomMessage):
        if message.type == "voice_call":
            breakout_room = message.message["breakout_room"]
            
            logger.info(f"joining breakout room {breakout_room}")
            
            def on_done(task: asyncio.Task):
                try:
                    task.result()
                except Exception as e:
                    logger.error(f"{e}", exc_info=e)

            task = asyncio.create_task(self.run_voice_agent(breakout_room=breakout_room))
            task.add_done_callback(on_done)
            
    
    async def _wait_for_disconnect(self, room: rtc.Room):
        disconnected = asyncio.Future()
        def on_disconnected(_):
            disconnected.set_result(True)
        room.on("disconnected", on_disconnected)

        logger.info("waiting for disconnection")
        await disconnected      

    def create_agent(self):
        return  Agent(
            instructions="\n".join(self.rules),
            allow_interruptions=True
        )     

        # agent = Agent(
        #    instructions="""
        #        You are a helpful assistant communicating through voice.
        #    """,
        #    stt=openai.STT(),
        #    llm=openai.LLM(model="gpt-4o"),
        #    tts=openai.TTS(),
        #    vad=silero.VAD.load(),
        #   allow_interruptions=True
        #)      

    def create_session(self) -> AgentSession:

        session = AgentSession(
            allow_interruptions=True,
            vad=silero.VAD.load(),
            stt=openai.STT(),
            tts=openai.TTS(voice="echo"),
            llm=openai.realtime.RealtimeModel(
                # it's necessary to turn off turn detection in the Realtime API in order to use
                # LiveKit's turn detection model
                voice="alloy",
                turn_detection=None,
                input_audio_transcription=None,

            ),
        )
        return session
    
    
    async def run_voice_agent(self, *, breakout_room: str):
        
        async with VoiceConnection(room=self.room, breakout_room=breakout_room) as connection:
            

            logger.info("starting voice agent")

            agent = self.create_agent()
            session = self.create_session()

            await session.start(agent=agent, room=connection.livekit_room)

            if self.auto_greet_prompt != None:
                session.generate_reply(user_input=self.auto_greet_prompt)

            if self.greeting != None:
                session.say(self.greeting)
            
            logger.info("started voice agent")
            await self._wait_for_disconnect(room=connection.livekit_room)
            


    

