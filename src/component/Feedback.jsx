import React,{ useState, useEffect } from 'react'
import '../App.css';
import Message from './Message';
import { API } from '@aws-amplify/api'
import * as queries from '../graphql/queries'

const Feedback = ({feedback}) => {
    //Determine if we should show the conversation log
    const [showMessage, setMessage] = useState(false);

    //messages in the conversation
    const [msgs,setConversation] = useState([]);

    //single feedback background color
    const [background, setBackground] = useState("#ffffff");

    //Set the inital state to not show conversation log
    useEffect(() => {
        setMessage(false);
      }, [feedback]);

    //get the conversation log by clicking the feedback
    const clickButton = async() => {
        if(!showMessage){
            const msg = await requestFeedbackById(feedback.id);
            const ms = JSON.parse(msg);
            console.log(ms);
            if(ms.length!==0){
                setConversation(ms);
                setMessage(!showMessage);
                console.log("fine");
            }
        }else{
            setMessage(!showMessage);
        }
    };

    //get conversation for specific feedback from backend
    const requestFeedbackById = async (id) => {
        let response;
        try {
          response = await API.graphql({
            query: queries.getFeedbackAPI,
            variables: {
              id
            }
          })
        } catch(err) {
          console.log(err);
        }
        
        return response.data.getFeedbackAPI.messages;
    }
    
    return( 
    <div className="single-Feedback" style={{ background: background }} onMouseEnter={() => setBackground("#DCDCDC")}
    onMouseLeave={() => setBackground("#ffffff")} onClick={clickButton}>
        <span>
            <img src="./user.png" height="30px" alt="user"/>
            <span className="in-line">{feedback.feedback}</span>
        </span>
        {showMessage &&
        <div>
            <p>Coversation Details:</p>
            <div className="feedback-messages">
                {msgs.map((message) => (
                    <Message message={message} key={msgs.indexOf(message)}/>
                ))}
            </div>
        </div>}
    </div>
    )
};

export default Feedback;