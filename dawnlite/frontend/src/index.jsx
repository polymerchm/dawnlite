import React from 'react';
import ReactDOM from 'react-dom';
import { createRoot } from 'react-dom/client'


// Somewhere in your `index.ts`:


import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { createRooot } from 'react-dom/client'
// import * as serviceWorker from "./serviceWorker";

const container = document.getElementById('root');
const root = createRoot(container); // createRoot(container!) if you use TypeScript
root.render(<App />);

// ReactDOM.render(
//     <App />,
//   document.getElementById('root')
// );

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
