from abc import ABC, abstractmethod
import zmq
import json
from enum import Enum
import asyncio
import zmq.asyncio
import threading
import sys
 
class ESignalType(Enum):
    START = 'start'
    STOP = 'stop'
    ON_CREATED = 'created'
    ON_STARTED = 'started'
    ON_STOPPED = 'stopped'
    ON_DESTROYED = 'destroyed'

class LifeCycleState(Enum):
    IN_ACTIVE = 1
    CREATED = 2
    STARTED = 3
    STOPPED = 4
    DESTROYED = 5

class SignalSocketResponses(Enum):
    SUCCESS = '200'
    SERVICE_UNAVAILABLE = '503'
    FAILURE = '400'

class Node(ABC):
    """
    Abstract base class for a node in a distributed system using ZeroMQ for communication.
    Each node can have multiple producers and consumers, and responds to lifecycle signals.
    """
    def __init__(self): 
        """
        Initialize the node with configuration from a JSON file.
        Expects the JSON file path as the first command line argument.
        Sets up ZMQ sockets for signal handling, producing, and consuming messages.
        """
        assert sys.argv.__len__() >= 2
        
        self.jsonFilePath = sys.argv[1]
        
        jsonFileData = open(self.jsonFilePath)
        self.jsonData =  json.load(jsonFileData)
        self.signalSocketIdentifier = self.jsonData["signalSocketIdentifier"]
        self.producerAddresses = self.jsonData["outputSocketIdentifiers"]
        self.consumerAddresses = self.jsonData["inputSocketIdentifiers"]
        self.producerPacketTypes = self.jsonData["outputSocketPacketTypes"]
        self.consumerPacketTypes = self.jsonData["inputSocketPacketTypes"]
        self.timeout = 1000  # 1 second timeout for polling

        self.lifeCycleState = LifeCycleState.CREATED

        self.context = zmq.Context(1)
        self.signalSocketContext = zmq.asyncio.Context()
        self.signalSocket = self.signalSocketContext.socket(zmq.REP)
        self.signalSocket.connect(self.signalSocketIdentifier)
        
        # Start the event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.thread = threading.Thread(target=self.start_event_loop)
        self.thread.start()
        
        # asyncio.create_task(self.initSignalSocket(self.signalSocket))
        self.consumerCount = len(self.consumerAddresses)
        self.producerCount = len(self.producerAddresses)

        self.poller = zmq.Poller()
        self.consumers = []
        for addr in self.consumerAddresses:
            sock = self.context.socket(zmq.SUB)
            sock.connect(addr)
            sock.setsockopt_string(zmq.SUBSCRIBE, "")
            self.poller.register(sock, zmq.POLLIN)
            self.consumers.append(sock)

        self.producers = []
        for addr in self.producerAddresses:
            sock = self.context.socket(zmq.PUB)
            sock.bind(addr)
            self.producers.append(sock)

        self.last_consumed = None
    
    def start_event_loop(self):
        task = self.loop.create_task(self.initSignalSocket(self.signalSocket))
        self.loop.run_forever()
    
    def isStreamStartable(self, lifeCycleState: LifeCycleState):
        return lifeCycleState == LifeCycleState.CREATED or lifeCycleState == LifeCycleState.STOPPED

    def isStreamStoppable(self, lifeCycleState: LifeCycleState):
        return lifeCycleState == LifeCycleState.STARTED

    async def initSignalSocket(self, signalSocket: zmq.Socket):
        while True:
            try:
                streamsEngineCommands = await signalSocket.recv_multipart()  # waits for msg to be ready
                msg = streamsEngineCommands[0].decode('utf-8')
                responseMsg = [SignalSocketResponses.SUCCESS.value, 'Success']
                if msg == ESignalType.START.value:
                    if self.isStreamStartable(self.lifeCycleState):
                        self.start()
                        responseMsg = [SignalSocketResponses.SUCCESS.value, 'Stream started successfully']
                    else:
                        responseMsg = [SignalSocketResponses.SERVICE_UNAVAILABLE.value, 'Stream already running']
                elif msg == ESignalType.STOP.value:
                    if self.isStreamStoppable(self.lifeCycleState):
                        self.stop()
                        responseMsg = [SignalSocketResponses.SUCCESS.value, 'Stream stopped successfully']
                    else:
                        responseMsg = [SignalSocketResponses.SERVICE_UNAVAILABLE.value, 'Stream not running']
                elif msg == ESignalType.ON_CREATED.value:
                    responseMsg = [SignalSocketResponses.SUCCESS.value, 'Stream node created successfully']
                else:
                    self.onSignal()
                    responseMsg = [SignalSocketResponses.SUCCESS.value, 'Signal processed successfully']
                multipart_msgs = [bytes(str_msg, 'utf-8') for str_msg in responseMsg]
                await signalSocket.send_multipart(multipart_msgs)
            except Exception as error:
                error_msg = [SignalSocketResponses.FAILURE.value, f'Error processing request: {str(error)}']
                try:
                    await signalSocket.send_multipart([bytes(msg, 'utf-8') for msg in error_msg])
                except Exception:
                    pass  # If we can't even send the error, there's not much we can do
    
    def start(self):    
        """
        Start the node's processing. Calls onStart() and updates lifecycle state.
        """
        self.onStart()
        self.lifeCycleState = LifeCycleState.STARTED
        
    def stop(self): 
        """
        Stop the node's processing. Calls onStop() and updates lifecycle state.
        """
        self.onStop()
        self.lifeCycleState = LifeCycleState.STOPPED
        
    def shutdown(self):
        """
        Shutdown the node completely. Calls onShutdown() and exits the process.
        """
        self.onShutdown()
        sys.exit()
    
    def consume(self):
        """
        Attempt to consume a message from any of the consumer sockets.
        
        Returns:
            int: 1 if message was consumed successfully, 0 if there was an error
        """
        try:
            socks = dict(self.poller.poll(self.timeout))
            for cons_num, consumer in enumerate(self.consumers):
                if socks.get(consumer) == zmq.POLLIN: 
                    if self.consumerPacketTypes[cons_num] == "multiPartString":
                        self.last_consumed = (cons_num, [bytes_msg.decode('utf-8') for bytes_msg in consumer.recv_multipart()])
                    elif self.consumerPacketTypes[cons_num] == "singlePartJSON":
                        self.last_consumed = (cons_num, json.loads(consumer.recv()))
                    return 1
        except Exception as e:
            print(e)
            return 0
    
    def produce(self, data, producerNum):
        """
        Produce a message on the specified producer socket.
        
        Args:
            data: The data to send (either a list of strings or a dictionary)
            producerNum (int): Index of the producer socket to use
            
        Returns:
            int: 1 if message was produced successfully, 0 if there was an error
        """
        if self.producerPacketTypes[producerNum] == "multiPartString":
            return self.produce_multiPartString(data, producerNum)
        elif self.producerPacketTypes[producerNum] == "singlePartJSON":
            return self.produce_singlePartJSON(data, producerNum)
    
    def produce_multiPartString(self, listOfStrings, producerNum):
        try:
            multipart_msg = [bytes(str_msg, 'utf-8') for str_msg in listOfStrings]
            self.producers[producerNum].send_multipart(multipart_msg)
        except Exception as e:
            print(e)
            return 0
        return 1
    
    def produce_singlePartJSON(self, dictionary, producerNum):
        try:
            msg = json.dumps(dictionary).encode('utf-8')
            self.producers[producerNum].send(msg)
        except Exception as e:
            print(e)
            return 0
        return 1
    
    @abstractmethod
    def onStart(self, *kwargs):
        pass
    
    @abstractmethod
    def onShutdown(self, *kwargs):
        pass
    
    @abstractmethod
    def onStop(self, *kwargs):
        pass
    
    @abstractmethod
    def onSignal(self, *kwargs):
        pass