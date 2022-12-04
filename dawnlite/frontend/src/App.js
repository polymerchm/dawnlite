
import './App.css'

import Header from './Components/Header'
import Light from './Components/Light'
import Alarm from './Components/Alarm'
import Footer from './Components/Footer'
// import useDimensions from 'react-use-dimensions'
import axios from 'axios'

// eslint-disable-next-line
import { Routes, Route, Link, BrowserRouter}  from "react-router-dom";
import { Stack, 
} from '@mui/material'


import {useEffect, useReducer, createContext, useState, useCallback} from 'react'
// import { fromDataBase  } from './Components/getAlarms'


export const $axios = axios.create({
  baseURL: 'http://127.0.0.1:5000'
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
  SET_BUSY_FLAG:          "set busy flag"
}



const initialState = {
  alarmList: Array(0), 
  brightness: 0, 
  currentEntry: null,
  listLoading: false,
  nextAlarm: "",
  busy: false
}



function reducer(state, action) {
  let newAlarmList
  let toUpdate
  switch (action.type) {
    case ACTIONS.SET_LIGHT_BRIGHTNESS:
      $axios.post('api/light', {level: action.payload}).catch(err => {console.log(err)})
      return {...state, brightness: action.payload}
    case ACTIONS.ALARM_ADD:
      if (state.alarmList === undefined || state.alarmList.length === 0) {
        newAlarmList =  [action.payload]
      } else {
        newAlarmList = [...state.alarmList, action.payload]
      }
      $axios.post('/api/alarm',action.payload).then(response => {}).catch(err => {console.log(err)})
      return {...state, alarmList: newAlarmList}
    case ACTIONS.ALARM_DELETE:
       newAlarmList = state.alarmList.filter( list => list.id !== action.payload)
       $axios.delete('/api/alarm/'+action.payload)
       .catch(err => {console.log(err)})
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
      .catch(err => {console.log(err)})
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
    return $axios.get('/api/alarm', {timeout: 2000})
  }

  const asyncDispatchNextAlarm = useCallback(() => {
    //setTimeout(()=>{}, 3000)
    retrieveNextAlarm().then(response => {
      dispatch({type: ACTIONS.SET_NEXT_ALARM, payload: response.data.alarm})
    })
  },[])

  const retrieveNextAlarm = () => { // returns a promise   
    return $axios.get('/api/nextAlarm')
  }



  // const asyncDispatchSetLight = () => {
  //   retrieveLight().then(response => {
  //     dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: response.data.level})
  //   })

  // }

  // const retrieveLight = () => {
  //   return $axios.get('/api/light')
  // }

  const onSync = useCallback(() => {
    $axios.get('/api/light')
    .then(result => {
        dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: result.data.level})
    })
    .catch(err => console.log(`Error after sync button handler Error=${err}`))
  },[])


  useEffect(() => { // only runs on initial call

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
          <Header level={state.brightness} dispatch={dispatch} nextAlarm={state.nextAlarm}
                  onSync={onSync}/>
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
              <Alarm alarmList={state.alarmList} listLoading={state.listLoading} dispatch={dispatch} onSync={onSync}
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
