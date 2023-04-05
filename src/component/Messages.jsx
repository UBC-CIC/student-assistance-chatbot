import React, { useEffect, useState } from "react";
import Message from './Message';
import '../App.css';
import {getMessage,addMessage} from "../variables";

import { Amplify, Interactions } from 'aws-amplify';
import { AWSLexV2Provider } from '@aws-amplify/interactions';
import interactionsConfig from "../../cdk/bin/cdk";

Amplify.addPluggable(new AWSLexV2Provider());

Amplify.configure(interactionsConfig);

const Messages = () => {
    //history of messages to be listed on the screen
    const [messages, setMessages] = useState([]);
    
    //button color
    const [background, setBackground] = useState("#072746");
    
    //send button state
    const [isSubmitting, setisSubmitting] = useState(false);
    
    //input from the user
    const [text, setText] = useState("");

    //check whether the send message is null or user is waiting for response
    const handleSend = async () => {
        if (isSubmitting === false && text !== "") {
            var message = {type:0, content:text};
            addMessage(message);
            const messageArray = [...messages];
            setMessages(messageArray);
            setText("");
            sendToLex(text);
            setisSubmitting(true);
        }else if(isSubmitting){
            alert("Please wait for a response from the chatbot before sending your next message...");
        }
    }

    //make scroll following the lastest message
    useEffect(() => {
        setMessages(getMessage());
        var objDiv = document.getElementById("messageview");
        objDiv.scrollTop = objDiv.scrollHeight;
      },[messages]);

    //make "Enter" button in the keyboard work
    const handleKeyDown = async (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSend();
        }
    }

    //send message to lex bot
    const sendToLex = async (text) =>{
        try {
            const response = await Interactions.send(interactionsConfig.Interactions.bots.ubcStudentAssistantBot.name, text);
            var res = response.messages;
            var message = {
                type: 1,
                content: res[0]['content']
            };

            addMessage(message);
            const messageArray = [...messages];
            setMessages(messageArray);
            setisSubmitting(false);
        } catch(err){
            var errorMessage = {
                type: 1,
                content:"We don't have the answer the for that right now. Please direct your question to academic advising. \n Here is the link: https://students.ubc.ca/enrolment/academic-learning-resources/academic-advising"
            };
            
            addMessage(errorMessage);
            const messageArray = [...messages];
            setMessages(messageArray);
            setisSubmitting(false);
            console.log(err);
        }
    }
    
    return (
        <div>
            <div className="messages" id="messageview">
                {messages.map((message) => (
                    <Message message={message} key={messages.indexOf(message)}/>
                ))}
            </div>
            <div className="InputBox">
                <span>
                <input data-testid="chat-page-title" className="input"  maxLength={200} type="text" placeholder="Type..."  onChange={(e) => setText(e.target.value)}  onKeyDown={handleKeyDown}
                value={text}/>
                <button disabled={isSubmitting} style={{ background: background }} onMouseEnter={() => setBackground("#00BFFF")}
      onMouseLeave={() => setBackground("#072746")} id="sendbutton" onClick={handleSend} className="send" type="submit">Send</button>
                </span>
            </div>
        </div>
    );
  };
  
  export default Messages;