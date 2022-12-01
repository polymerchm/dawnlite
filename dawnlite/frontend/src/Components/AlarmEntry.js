import React from 'react'
import 'rc-time-picker/assets/index.css';
import  AlarmListItem  from './AlarmListItem'
import { defaultAlarm } from './getAlarms'


const AlarmEntry = ({ setCreateNewAlarmFlag, addAlarm, dispatch}) => {

    return (
           <AlarmListItem 
                    isList={false} 
                    setCreateNewAlarmFlag={setCreateNewAlarmFlag} 
                    addAlarm={addAlarm}
                    alarmListItem={defaultAlarm}
                    dispatch={dispatch}
                    />

  
    )
};

export default AlarmEntry