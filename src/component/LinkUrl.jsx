import React from 'react'
import '../App.css';

const LinkUrl = ({message}) => {
    //change the format of return response and add url link function to returned link
    if (message.before === "\n\n\n" || message.before === "\n") {
        return;
    }

    if (!message.url){
        return (message.before);
    }

    var content;

    if(message.before.substring(0,3) === "\n\n\n"){
        content = message.before.substring(3);
    }else{
        content = message.before;
    }

    return(<div className="p1"> {content} <a className="url" href={message.url} target="_blank" rel="noreferrer"> Reference Link</a> </div>);
};

export default LinkUrl;