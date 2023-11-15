
import './App.css'

import Header from './Components/Header'
import Light from './Components/Light'
import Alarm from './Components/Alarm'
import Footer from './Components/Footer'
import axios from 'axios'


import {  Routes, 
          Route, 
          BrowserRouter}  from "react-router-dom";
import { Stack, 
} from '@mui/material'


import {useEffect, useReducer, createContext, useState, useCallback} from 'react'

const flask_server_url = 'http://127.0.0.1:5000'

// GLOBAL CONSTANTS
export const $axios = axios.create({
  baseURL: flask_server_url
}) 


$axios.defaults.headers = {
  'Cache-Control': 'no-cache',
  'Pragma': 'no-cache',
  'Expires': '0',
};

export const AppContext = createContext()

export const ACTIONS = {
  CHANGE_ALARM_TIME:      "change_alarm_time",
  CHANGE_ALARM_REPEAT:    "change_alarm_repeat",
  CHANGE_ALARM_DURATION:   "change_alarm_duration",
  CHANGE_ALARM_NTENSITY:  "change_alarm_intensity",
  CHANGE_ALARM_ENABLED:   "change_alarm_enabled",
  ALARM_DELETE:           "alarm_delete",
  ALARM_UPDATE:           "alarm_update",
  ALARM_ADD:              "alarm_add",
  SET_LIGHT_BRIGHTNESS:   "set_light_brightness",
  INITIALIZE_ALARMS:      "initialize_alarms",
  LOADING:                "loading",
  FORCE_LIGHT_STATE:      "force light",
  SET_NEXT_ALARM:         "set next alarm",
  SET_BUSY_FLAG:          "set busy flag",
  PULSE:                  "set pulsee"
}



const initialState = {
  alarmList: Array(0), 
  brightness: 0, 
  currentEntry: null,
  listLoading: false,
  nextAlarm: "",
  busy: false,
  pulse: 0
}



function reducer(state, action) {
  let newAlarmList
  let toUpdate
  switch (action.type) {
    case ACTIONS.SET_LIGHT_BRIGHTNESS:
      $axios.post('/api/light', {level: action.payload}).catch(err => {console.log(`SET_LIGHT_BRIGHTNESS POST ${err}`)})
      return {...state, brightness: action.payload}
    case ACTIONS.ALARM_ADD:
      if (state.alarmList === undefined || state.alarmList.length === 0) {
        newAlarmList =  [action.payload]
      } else {
        newAlarmList = [...state.alarmList, action.payload]
      }
      $axios.post('/api/alarm',action.payload).then(response => {}).catch(err => {console.log(`ADD_ALARM POST ${err}`)})
      return {...state, alarmList: newAlarmList}
    case ACTIONS.ALARM_DELETE:
       newAlarmList = state.alarmList.filter( list => list.id !== action.payload)
       $axios.delete('/api/alarm/'+action.payload)
       .catch(err => {console.log(`ALARM_DELETE DELETE ${err}`)})
      return { ...state, alarmList: newAlarmList}
    case ACTIONS.ALARM_UPDATE:
      // should  check here for overlap
      newAlarmList = state.alarmList.map(item => {
        if (item.id === action.payload.id) {
          toUpdate = action.payload
          return action.payload //replace with updated
        } else {
          return item
        }
      })
      $axios.patch('/api/alarm', toUpdate)
      .catch(err => {console.log(`ALARM_UPDATE PATCH ${err}`)})
      return {...state, alarmList: newAlarmList}
    case ACTIONS.LOADING:
      return { ...state, listLoading: true}
    case ACTIONS.INITIALIZE_ALARMS:
        return  {...state, listLoading: false, alarmList: action.payload}
    case ACTIONS.FORCE_LIGHT_STATE:
        return  {...state, brightness: action.payload}
    case ACTIONS.SET_NEXT_ALARM:
        return {...state, nextAlarm: action.payload}
    case ACTIONS.SET_BUSY_FLAG:
        return {...state, busy: action.payload}
    case ACTIONS.PULSE:
        return {...state, pulse: action.payload}
    default:
      return state
  }
}



function App() {

  const [state, dispatch] = useReducer(reducer, initialState)
  const [busy, setBusy] = useState(false)
  

  const asyncDispatch = () => {
    dispatch({ type: ACTIONS.LOADING})
    setTimeout(()=>{}, 3000)
    retrieveAlarmList().then(response => {
      dispatch({type: ACTIONS.INITIALIZE_ALARMS, payload: response.data})
    })
  }

  const retrieveAlarmList = () => { // returns a promise   
    return $axios.get('/api/alarms')
  }

  const asyncDispatchNextAlarm = () => {
    //setTimeout(()=>{}, 3000)
    retrieveNextAlarm().then(response => {
      dispatch({type: ACTIONS.SET_NEXT_ALARM, payload: response.data.alarm})
    })
  }

  const retrieveNextAlarm = () => { // returns a promise   
    return $axios.get('/api/nextAlarm')
  }

//  this one setups up for the SSE 
  
  useEffect(() => { // runs on mount 

    const sse = new EventSource(flask_server_url + '/api/stream')

    sse.addEventListener('pulse', (e) => {
      dispatch({type: ACTIONS.PULSE, payload: e.data})
    })

    sse.addEventListener('light_change', (e)=> {
      dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: e.value})
    })

    sse.addEventListener('next_alarm', (e) => {
      dispatch({type: ACTIONS.SET_NEXT_ALARM, payload: e.data})
    })

    sse.onerror = (e) => {
      console.log(`On Error Fired ${e}`)
      sse.close()
    }

    return (e) => {
      sse.close()
    }

  })



  useEffect(() => { // only runs on initial call, set things up
    console.log("in the  useeffect")

    async function getLightInfo() {
      try {
        let response = await $axios.get('/api/light')
        dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: response.data['level'] || 100})
      }
      catch (err) {
        console.log("in useEffect getLightInfo",err)
      }
    }
    getLightInfo()
    asyncDispatch()
    asyncDispatchNextAlarm()
  }, [])

  //TODO:    determine if the configuration files exist

 
  return (
    <BrowserRouter className="App">
      <Stack direction="column"
          spacing={{sx:2, sm: 3, md:5}}
      >
          <Header level={state.brightness}  nextAlarm={state.nextAlarm}/>
          <Routes>
            <Route exact path="/" element={
                <Light brightness={state.brightness} dispatch={dispatch}/>
              } 
            />
            <Route path="/light" element={
              <Light brightness={state.brightness} dispatch={dispatch}/>
              } 
            />
            <Route path="/alarm" element={
              <Alarm alarmList={state.alarmList} 
                      listLoading={state.listLoading} 
                      dispatch={dispatch}
                      asyncDispatch={asyncDispatchNextAlarm}
                      
                                />
            }
            />
          </Routes>
          <Footer/>
      </Stack>
    </BrowserRouter>
  )
}


export default App;
