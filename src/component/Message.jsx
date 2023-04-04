import React from 'react'
import '../App.css';
import LinkUrl from './LinkUrl';


const Message = ({ message }) => {

    //search for url link and append the link to a message
    const AddLink = (str) => {
        if (str !== null) {
            const link =/https:\/\/([\w-]+\S)+[\w-]+([\w-?%#&=]*)?(\/[\w- ./?!~:,()%#&=]*)?/g;
            var beforeUrl = str.split(link);
            var url = str.match(link);
            var contents = [];

            if (url === null) {
                return [{"before":str,"url":null}];
            }
             
            for (var i = 0; i < beforeUrl.length; i = i+4){
                if (url[i/4] == null) {
                    contents.push({"before":beforeUrl[i],"url":null});
                } else {
                    contents.push({"before":beforeUrl[i],"url":url[i/4]});
                }
            }
            return contents;
        }

        return [{"before":str,"url":null}];
    };

    var contents = AddLink(message.content);

    //format of message from user
    if (message.type === 0) {
        return (
           <div className="userMessage">
                <div className="messageInfo">
                    <img src="./user.png" height="35px" alt="user"/>
                </div>
                <div className="userContent">
                    <div className="p2">{message.content}</div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="message">
            <div className="messageInfo">
                <img src="./chat-bot.png" height="40px" alt="chatbot"/>
            </div>
            <div className="messageContent">
                <div className="p1"> 
                        {contents.map((message) => (
                                <LinkUrl message={message} key={contents.indexOf(message)}/>
                                ))}
                </div>
            </div>
        </div>
    );
  };
  
  export default Message;