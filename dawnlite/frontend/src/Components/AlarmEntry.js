import React from 'react'
import { useState } from 'react'
import  { Card, 
    CardContent, 
    CardActions, 
    Button,
    Checkbox, 
    Typography, 
    Box, 
    Grid, 
    Select, 
    MenuItem, 
    InputLabel, 
    
} from '@mui/material'


import FormControlLabel from '@mui/material/FormControlLabel';
import TimePicker from 'rc-time-picker';
import 'rc-time-picker/assets/index.css';
import moment from 'moment'
import { uuid } from '../uuid'
import { repeatDayData } from './repeatDays' 
import  AlarmListItem  from './AlarmListItem'


const AlarmEntry = (props) => {

    const setAlarmState = props.setAlarmState

    const changeRepeatDay = (alarm) => (e) => {
        setRepeatDays(repeatDays ^ alarm.bit) // xor
    }

    const onTimeChanged =  (value)  => {
        setAlarmTime(value)
    }

    const onDurationChange = (e) => {
        setDuration(e.target.value)
    }

    const onIntensityChange = (e) => {
        setIntensity(e.target.value)
    }

    const onSave = (e)  => {
        // setTimeStamp(Date())
        props.alarmStateSet(false)
        //look for a similar alarm
        // if redundant, warn
        // if not, save it.
        // and force an update.
        console.log(getAlarm())

    }

    const getAlarm = () => {
        return {date: moment(timeStamp).format('YYYY-MM-DD HH:MM:SS'), alarm: alarmTime.format("HH:mm"), repeat: repeatDays, duration: duration, intensity: intensity, id: uuid()}
    }

    const onCancel = (e) => {
        props.alarmStateSet(false)
    }

    
    const [timeStamp, setTimeStamp] = useState(Date())
    const [alarmTime, setAlarmTime] = useState(moment()); 
    const [repeatDays, setRepeatDays] = useState(0);
    const [duration, setDuration] = useState(20) // 20 minutes
    const [intensity, setIntensity] = useState(25) // 25%
   
    const [alarmObject, setAlarmObject] = useState({})

    return (
           <AlarmListItem 
                    isList={false}
                    updateObjects={setAlarmObject} setAlarmState={setAlarmState}
                    />

  
    )
};

export default AlarmEntry