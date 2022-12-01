// import React from 'react'
// import momemt from 'moment'
// import { uuid } from '../uuid'



export const defaultAlarm = () => {
    return {time: '08:00', 
            repeatDays: 0, 
            alarmDuration: 20, 
            rampDuration: 3,
            level: 25, 
            id: '', 
            enabled: true
        }
    }   

export const fromDataBase = (alarms) => { // list of alarms

    return alarms.map (alarm => {
        return {
            time: alarm.time, 
            repeatDays: alarm.repeatDays, 
            alarmDuration: alarm.alarmDuration,
            rampDuration: alarm.rampDuration,
            level: alarm.level, 
            id: alarm.id, 
            enabled: alarm.enabled
        }
    })
}

