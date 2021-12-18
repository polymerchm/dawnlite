// import React from 'react'
// import momemt from 'moment'
import { uuid } from '../uuid'


const getAlarms = () => {
    return [
        {date: '2021-12-31 01:01:01', alarmTime: '08:00', repeat: 10, duration: 20, intensity: 25, id: uuid()},
        {date: '2021-12-31 01:01:01', alarmTime: '09:00', repeat: 0, duration: 45, intensity: 50, id: uuid()},
        {date: '2021-12-31 01:01:01', alarmTime: '10:00', repeat: 13, duration: 20, intensity: 100, id: uuid()},
        {date: '2021-12-31 01:01:01', alarmTime: '16:00', repeat: 25, duration: 120, intensity: 100, id: uuid()},
        {date: '2021-12-31 01:01:01', alarmTime: '23:00', repeat: 33, duration: 60, intensity: 75, id: uuid()},
    ]
}


export default getAlarms;