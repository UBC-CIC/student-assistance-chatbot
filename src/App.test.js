import { render, screen, fireEvent, waitFor} from '@testing-library/react';
import ChatPage from './page/ChatPage'
import AdminPage from './page/AdminPage'
import FeedbackPage from './page/FeedbackPage';
import {BrowserRouter, Route, Routes } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import awsmobile from './aws-exports';

Amplify.configure(awsmobile);

describe('Check ChatPage Function', () => {
  jest.setTimeout(20000);
  beforeEach(() => {
    render(
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/feedback" element={<FeedbackPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </BrowserRouter>
    );
  });

  test('check chat page', () => {
    const titleElement = screen.getByText(/student assistant bot/i);
    expect(titleElement).toBeInTheDocument();
  
    const adminButton = screen.getByRole('button', { name: /admin/i });
    expect(adminButton).toBeInTheDocument();
  
    const feedbackButton = screen.getByRole('button', { name: /feedback/i });
    expect(feedbackButton).toBeInTheDocument();
  
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeInTheDocument();
  });

  test('verify response message', async () => {
    const input = screen.getByTestId("chat-page-title");
    fireEvent.change(input, { target: { value: 'cpen400p' } });
    expect(input.value).toBe('cpen400p');

    const button = screen.getByText(/send/i);
    fireEvent.click(button);

    expect(screen.getByText('cpen400p')).toBeInTheDocument();

    await new Promise(resolve => setTimeout(resolve, 5000));
    expect(screen.getByText(/For cpen400p, we found the following information/i)).toBeInTheDocument();
  });

  test('should open feedback page when button clicked', async() => {
  
    const button = screen.getByRole('button', { name: /feedback/i });
    fireEvent.click(button);
  
    await waitFor(() => {
      expect(screen.getByText(/Please enter a rating based on the satisfaction of your experience with the chatbot/i)).toBeInTheDocument();
    });
  });
  
  
  test('should open admin page when button clicked', async() => {
    const button1 = screen.getByRole('button', { name: /back/i });
    fireEvent.click(button1);

    const button = screen.getByRole('button', { name: /admin/i });
    fireEvent.click(button);
  
    await waitFor(() => {
      expect(screen.getByText(/Admin Dashboard/i)).toBeInTheDocument();
    });

    const button2 = screen.getByRole('button', { name: /back/i });
    fireEvent.click(button2);
  });
});

describe('Check FeedbackPage Function', () => {
  jest.setTimeout(20000);
  beforeEach(() => {
    render(
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/feedback" element={<FeedbackPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </BrowserRouter>
    );
  });

  test('check feedback page', () => {
    const button = screen.getByRole('button', { name: /feedback/i });
    fireEvent.click(button);

    const titleElement = screen.getByText(/Feedback/);
    expect(titleElement).toBeInTheDocument();
  
    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    const rateStar = screen.getByTestId("rate-star");
    expect(rateStar).toBeInTheDocument();

    const feedbackContent = screen.getByTestId("feedback-content");
    expect(feedbackContent).toBeInTheDocument();
  
    const submitButton = screen.getByRole('button', { name: /submit/i });
    expect(submitButton).toBeInTheDocument();
  
    expect(screen.getByText(/Please enter a rating based on the satisfaction of your experience with the chatbot/i)).toBeInTheDocument();
  });

  test('send empty feedback', async() => {
    window.alert = jest.fn(() => true);
    const feedbackContent = screen.getByTestId("feedback-content");
    fireEvent.change(feedbackContent, { target: { value: '' } });
    expect(feedbackContent.value).toBe('');
  
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
    expect(window.alert).toHaveBeenCalledWith("You can't submit blank feedback.");
  });

  test('send feedback successfully', async() => {
    window.alert = jest.fn(() => true);
    const feedbackContent = screen.getByTestId("feedback-content");
    fireEvent.change(feedbackContent, { target: { value: "Test Feedback" } });
    expect(feedbackContent.value).toBe("Test Feedback");
  
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
  
    await new Promise(resolve => setTimeout(resolve, 6000));

    //looks like Jest unable to call API correctly
    expect(window.alert).toHaveBeenCalledWith("Send Successfully!");
    expect(screen.getByText(/student assistant bot/i)).toBeInTheDocument();
    
  });
});

describe('Check AdminPage Function', () => {
  jest.setTimeout(20000);

  beforeEach(() => {
    render(
      <BrowserRouter>
        <AdminPage />
      </BrowserRouter>
    );
  });

  test('check admin page', async() => {
    
    const titleElement = screen.getByText(/Admin Dashboard/i);
    expect(titleElement).toBeInTheDocument();

    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    await new Promise(resolve => setTimeout(resolve, 5000));
    const emailInput = screen.getByLabelText('Username');
    expect(emailInput).toBeInTheDocument();

    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toBeInTheDocument();

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    expect(submitButton).toBeInTheDocument();
  });

  test('check admin login function', async() => {
    //Enter your own admin username and password for testing purposes
    const state = {
      username:'',
      password:'' 
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
    const emailInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: state.username } });
    fireEvent.change(passwordInput, { target: { value: state.password } });

    // Click the submit button
    fireEvent.click(submitButton);
    await new Promise(resolve => setTimeout(resolve, 7000));
    expect(screen.getByText(/sign out/i)).toBeInTheDocument();
  });

  test('check feedbacks after log in', async() => {
    await new Promise(resolve => setTimeout(resolve, 5000));
    const feedbacks = screen.getAllByText(/test/i);
    expect(feedbacks[0]).toBeInTheDocument();
  });

  test('check switched feedback and coversation log when click feedback', async() => {
    const rate5 = screen.getByTestId("rate-5-button");
    fireEvent.click(rate5);

    await new Promise(resolve => setTimeout(resolve, 10000));
    const feedbacks = screen.getAllByText(/test feedback/i);
    expect(feedbacks[0]).toBeInTheDocument();

    fireEvent.click(feedbacks[0]);

    await new Promise(resolve => setTimeout(resolve, 2000));
    const convo = screen.getByText(/Hello, welcome to UBC's prototype chatbot!/i);
    expect(convo).toBeInTheDocument();

    await new Promise(resolve => setTimeout(resolve, 2000));
    fireEvent.click(feedbacks[0]);
    expect(convo).not.toBeInTheDocument();
  });

  test('test sign out',async() => {
    const signout = screen.getByText(/sign out/i);
    fireEvent.click(signout);

    await new Promise(resolve => setTimeout(resolve, 7000));
    const emailInput = screen.getByLabelText('Username');
    expect(emailInput).toBeInTheDocument();

    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toBeInTheDocument();

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    expect(submitButton).toBeInTheDocument();

  });

});


