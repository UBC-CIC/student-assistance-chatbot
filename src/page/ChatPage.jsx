import React,{ useState } from 'react'
import '../App.css'
import Messages from '../component/Messages'
import { useNavigate } from 'react-router-dom'


const ChatPage = () => {
  const [background, setBackground] = useState("#2c5b7b");
  const [adminbackground, setadminBackground] = useState("#2c5b7b");

  let navigate = useNavigate();
  
  //route to provide feedback
  const routeChangetoFeedback = () =>{ 
    let path = `/feedback`; 
    navigate(path);
  }

  //route to open admin page
  const routeChangetoAdmin = () =>{ 
    let path = `/admin`; 
    navigate(path);
  }

  return (
    <div className="App">
      <header className="App-header">
        <span>
            <img src="./ubcdarklogo.png" height="60vh" alt="logo"/>
            <span className='App-name'>Student Assistant Bot</span>
            <button style={{ background: adminbackground }} onMouseEnter={() => setadminBackground("#00BFFF")}
      onMouseLeave={() => setadminBackground("#2c5b7b")} onClick={routeChangetoAdmin} className="admin-button">Admin</button>
            <button style={{ background: background }} onMouseEnter={() => setBackground("#00BFFF")}
      onMouseLeave={() => setBackground("#2c5b7b")} onClick={routeChangetoFeedback} className="fB">Feedback</button>
        </span>
      </header>

      <Messages />
    </div>
  )
}

export default ChatPage