import React,{ useEffect, useState } from 'react'
import '../App.css'
import { useNavigate } from 'react-router-dom'
import { Authenticator } from '@aws-amplify/ui-react'
import '../styles.css'
import { API } from '@aws-amplify/api'
import * as queries from '../graphql/queries'
import Feedback from '../component/Feedback'

const AdminPage = () => {
  //back button color
  const [background, setBackground] = useState("#2c5b7b");
  
  //feedbacks displayed on the page
  const [feedbacks, setFeedback] = useState([]);
  
  //switch button color
  const [color1, set1Color] = useState("#072746");
  const [color2, set2Color] = useState("#072746");
  const [color3, set3Color] = useState("#072746");
  const [color4, set4Color] = useState("#072746");
  const [color5, set5Color] = useState("#072746");
  
  //shown what rating the displayed feedbacks are
  const [page,setPage] = useState(0);
  let navigate = useNavigate(); 
  
  //back to chat page
  const routeChange = () =>{ 
    let path = `/`; 
    navigate(path);
  }
  
  //get all feedback filtered by the star rating
  const requestFeedbackByRating = async (rating) => {
    const filter = { rating: { eq: rating} };
    const data = [];
    let response;
    try {
      response = await API.graphql({
        query: queries.listFeedbackAPIS,
        variables: {
          filter,
        }
      });

      data.push(...response.data.listFeedbackAPIS.items);

      //Pagination
      let nextToken = response.data.listFeedbackAPIS.nextToken;
      while(nextToken) {
        response = await API.graphql({
          query: queries.listFeedbackAPIS,
          variables: {
            filter,
            nextToken
          }
        });
        data.push(...response.data.listFeedbackAPIS.items);
        nextToken = response.data.listFeedbackAPIS.nextToken;
      }
    } catch(err) {
      console.log(err);
    }
    return data;
  }

  //get 5 star feedbacks
  const getFeedback = async() =>{
    const fb = await requestFeedbackByRating(5);
    console.log(fb);
    setFeedback(fb);
    setPage(5);
    set5Color("#00BFFF");
    set2Color("#072746");
    set3Color("#072746");
    set4Color("#072746");
    set1Color("#072746");
  }

  //get 4 star feedbacks
  const get4Feedback = async() =>{
    const fb = await requestFeedbackByRating(4);
    console.log(fb);
    setFeedback(fb);
    setPage(4);
    set4Color("#00BFFF");
    set2Color("#072746");
    set3Color("#072746");
    set1Color("#072746");
    set5Color("#072746");
  }

  //get 3 star feedbacks
  const get3Feedback = async() =>{
    const fb = await requestFeedbackByRating(3);
    console.log(fb);
    setFeedback(fb);
    setPage(3);
    set3Color("#00BFFF");
    set2Color("#072746");
    set1Color("#072746");
    set4Color("#072746");
    set5Color("#072746");
  }

  //get 2 star feedbacks
  const get2Feedback = async() =>{
    const fb = await requestFeedbackByRating(2);
    console.log(fb);
    setFeedback(fb);
    setPage(2);
    set2Color("#00BFFF");
    set1Color("#072746");
    set3Color("#072746");
    set4Color("#072746");
    set5Color("#072746");
  }

  //get 1 star feedbacks
  const get1Feedback = async() =>{
    const fb = await requestFeedbackByRating(1);
    console.log(fb);
    setFeedback(fb);
    setPage(1);
    set1Color("#00BFFF");
    set2Color("#072746");
    set3Color("#072746");
    set4Color("#072746");
    set5Color("#072746");
  }

  //set 1 star feedback as initial state
  useEffect(() => {get1Feedback()},[]);

  return(
    <div className="App">
      <header className="App-header">
        <span>
            <img src="./ubcdarklogo.png" height="60vh" alt="ubc-logo"/>
            <span className='App-name'>Admin Dashboard</span>
            <button style={{ background: background }} onMouseEnter={() => setBackground("#00BFFF")}
            onMouseLeave={() => setBackground("#2c5b7b")} onClick={routeChange} className="fB">Back</button>
        </span>
      </header>

        <Authenticator className='auth'>
            {({signOut}) => (
              <div className="feedbackpage">
                <div className='rate-page'>
                  <div className="choose-rate" style={{ background: color1 }} onMouseEnter={() => set1Color("#00BFFF")}
      onMouseLeave={() => {if(page!==1)set1Color("#072746")}} onClick={get1Feedback}><img className="pic" src="./stars/one.png" alt="1 star" height="30px"/></div>
                  <div className="choose-rate" style={{ background: color2 }} onMouseEnter={() => set2Color("#00BFFF")}
      onMouseLeave={() => {if(page!==2)set2Color("#072746")}} onClick={get2Feedback}><img className="pic" src="./stars/two.png" alt="2 star" height="30px"/></div>
                  <div className="choose-rate" style={{ background: color3 }} onMouseEnter={() => set3Color("#00BFFF")}
      onMouseLeave={() => {if(page!==3)set3Color("#072746")}} onClick={get3Feedback}><img className="pic" src="./stars/three.png" alt="3 star" height="30px"/></div>
                  <div className="choose-rate" style={{ background: color4 }} onMouseEnter={() => set4Color("#00BFFF")}
      onMouseLeave={() => {if(page!==4)set4Color("#072746")}} onClick={get4Feedback}><img className="pic" src="./stars/four.png" alt="4 star" height="30px"/></div>
                  <div className="choose-rate" data-testid="rate-5-button" style={{ background: color5 }} onMouseEnter={() => set5Color("#00BFFF")}
      onMouseLeave={() => {if(page!==5)set5Color("#072746")}} onClick={getFeedback}><img className="pic" src="./stars/five.png" alt="5 star" height="30px"/></div>
                  <button className="signout" onClick={signOut}>Sign out</button>
                </div>
                <div className="allfeedback">
                  {feedbacks.map((f) => (
                      <Feedback feedback={f} key={feedbacks.indexOf(f)}></Feedback>
                  ))}
                </div>
              </div>
                
            )}
        </Authenticator>
    </div>
  );

  
}

export default AdminPage