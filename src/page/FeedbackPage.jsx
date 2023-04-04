import { API } from '@aws-amplify/api'
import * as mutations from '../graphql/mutations'
import { allMessages } from  '../variables'
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom'
import { Rating } from 'react-simple-star-rating'

const FeedbackPage = () => {
    //Feedback Content
    const [text, setText] = useState("");
    //Rate for bot
    const [rating, setRating] = useState(5);
    //Back button color
    const [background, setBackground] = useState("#2c5b7b");
    //Submit button color
    const [buttonColor, setColor] = useState('red');

    //set the rate
    const handleRating = (rate) => {
        setRating(rate)
    }

    let navigate = useNavigate(); 
    //back to chat page
    const routeChange = () =>{ 
        let path = `/`; 
        navigate(path);
    }

    //send feedback to backend
    const handleFeedback = async () => {
        const inputDetails = {
            messages: JSON.stringify(allMessages),
            feedback: text,
            rating
        }  

        if (rating === 0 || text === "") {
            alert("You can't submit blank feedback.")
            return;
        }

        try {
            const response = await API.graphql({
                query: mutations.createFeedbackAPI,
                variables: {
                    input: inputDetails
                }
            })
            console.log(response);
            routeChange();
        } catch(err){
            console.log(err);
            alert("Please try to submit your feedback again!");
            routeChange();
        }
    }

    return (
      <div className="App">
        <header className="App-header">
          <span>
              <img src="./ubcdarklogo.png" height="60vh" alt="logo"/>
              <span className='App-name'>Feedback</span>
              <button style={{ background: background }} onMouseEnter={() => setBackground("#00BFFF")}
      onMouseLeave={() => setBackground("#2c5b7b")} onClick={routeChange} className="fB">Back</button>
          </span>
        </header>

        <div>
            <div data-testid="rate-star">
                <p className="rateTxt">Please enter a rating based on the satisfaction of your experience with the chatbot:</p>
                <Rating className="ratestar" onClick={handleRating} initialValue={rating} size={30}/>
            </div>
            <p className="feedbackTxt">Please enter any feedback you may have for the quality of the chatbot's responses or any other comments:</p>
            <textarea data-testid="feedback-content" className="feedbackContent" maxLength={800} placeholder="Type Here..."  onChange={(e) => setText(e.target.value)}
                value={text}/>
            <br></br>
            <button style={{ background: buttonColor }} onMouseEnter={() => setColor("#F08080")}
      onMouseLeave={() => setColor('red')} onClick={handleFeedback} className="submit">Submit</button>
        </div>
      </div>
    )
}

export default FeedbackPage

