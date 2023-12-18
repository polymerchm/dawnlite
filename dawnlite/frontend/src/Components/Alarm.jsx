import React from 'react' 
import { useState } from 'react'
import  {   Stack, 
            Button, 
            Box 
        }  from '@mui/material'
import AlarmEntry from './AlarmEntry'
import AlarmList from './AlarmList'
import InvalidAlarmEntry from './InvalidAlarmEntry'
import moment from 'moment'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import { ACTIONS } from '../App'

 



const Alarm = ({alarmList, listLoading, dispatch, alert, asyncDispatch}) => {

    
    const [createNewAlarmFlag, setCreateNewAlarmFlag] = useState(false)
    const [workingAlarm, setWorkingAlarm] = useState({}) // working alarmObject for entry
    const [invalidEntryOpen, setInvalidEntryOpen] = useState(false)

    const isInvalidAlarmEntry = (alarm, modifying=false) => {

        // first check for missing days

        if (alarm.repeatDays === undefined || alarm.repeatDays === 0) {
            dispatch({type: ACTIONS.SET_ALERT, payload: {show: true, type: 'nodays', value: null}})
            return true
        }

        // check to see alarm overlaps with any other
        
        const alarmStart = moment(alarm.time, "HH:mm")  // seconds since epoch
        const alarmEnd = moment(alarmStart).add(alarm.alarmDuration, 'minutes')
        const alarmRepeatDays = alarm.repeatDays
        const alarmEnabled = alarm.enabled
        const alarmID = alarm.id
        if (alarmList === undefined || alarmList.length === 0) {
            return false // don't waste time
        }
        if (!alarmEnabled) {  // don't bother here if new one not enabled.   catch overlap if it gets enabled
            return false
        }
      
        for (let entry of alarmList) {
            if (modifying && entry.id === alarmID) {  // don't check against self
                continue
            }
            if (!entry.enabled) {  // again don't wast time
                continue
            }

            let haveCommonRepeatDays = alarmRepeatDays & entry.repeatDays
            if (!haveCommonRepeatDays) { // not the same day or both not repeating
                continue
            }
            const entryStart = moment(entry.time, "HH:mm") 
            const entryEnd = moment(entryStart).add(entry.alarmDuration, 'minutes')
            let startsInside = alarmStart.isBetween(entryStart, entryEnd, null, '[)')
            let endsInside = alarmEnd.isBetween(entryStart, entryEnd, null, '(]')
            let encloses = alarmStart.isBefore(entryStart)  && alarmEnd.isAfter(entryEnd)
            if ( startsInside || endsInside || encloses) {
                dispatch({type: ACTIONS.SET_ALERT, payload: {show: true, type: 'overlap', value: entry.time}})
                return true  // there is an overlap
            }
        }
        return false
    } 
    
 
    const addAlarm = (newAlarm)  => {
        // test here for an overlapping alarm
        // if valid, add it
        //if not, put up a warning and ignore
        if (!isInvalidAlarmEntry(newAlarm)) {
            dispatch({type: ACTIONS.ALARM_ADD, payload: newAlarm})
            asyncDispatch()
            setWorkingAlarm({})
        }
    }



    const updateAlarmList = (targetAlarm, shouldDelete)  => {
        const alarmID = targetAlarm.id
        let isOkay = true
        if (shouldDelete) {  
            // confirm the item pointed to by teh index matched the date 
            dispatch({type: ACTIONS.ALARM_DELETE, payload: alarmID})
        } else { // update
            // check to see if the changes don;t cause a conflict
            if (isInvalidAlarmEntry(targetAlarm, true)) {
                isOkay= false
            } else {
                dispatch({type: ACTIONS.ALARM_UPDATE, payload: targetAlarm})
            }
        }
        asyncDispatch()
        return isOkay
    }

    return(
        // a new alarm box
        // list of current
      
        <Stack direction="column" spacing={{sx:2, sm: 3, md:5}}>
           <Accordion expanded={createNewAlarmFlag}>
                <AccordionSummary
                    // expandIcon={<ExpandMoreIcon />}
                    aria-controls="panel1a-content"
                    id="panel1a-header"
                >
                {createNewAlarmFlag ? null : 
                    <Box m="auto" ><Button onClick={()=> setCreateNewAlarmFlag(true)}>New Alarm</Button></Box> 
                }
                </AccordionSummary>
                <AccordionDetails>
                    <AlarmEntry  setCreateNewAlarmFlag={setCreateNewAlarmFlag} 
                        addAlarm={addAlarm} dispatch={dispatch}
                    />
                </AccordionDetails>
            </Accordion>
            
         
            {listLoading ? <h4>Alarms Loading.....</h4> :
            <AlarmList alarmList={alarmList} updateAlarmList={updateAlarmList}/> }

            <InvalidAlarmEntry alert={alert} dispatch={dispatch}/>
            <h1>  </h1>
            
        </Stack>
     
    )
}

export default React.memo(Alarm)