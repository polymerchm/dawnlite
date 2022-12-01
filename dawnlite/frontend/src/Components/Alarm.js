import { useState, useEffect } from 'react'
import  { Stack, Button, Box }  from '@mui/material'
import AlarmEntry from './AlarmEntry'
import AlarmList from './AlarmList'
import InvalidAlarmEntry from './InvalidAlarmEntry'
import moment from 'moment'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import { ACTIONS } from '../App'

 



const Alarm = ({alarmList, listLoading, dispatch, $axios, asyncDispatch, onSync}) => {

    
    const [createNewAlarmFlag, setCreateNewAlarmFlag] = useState(false)
    const [workingAlarm, setWorkingAlarm] = useState({}) // working alarmObject for entry
    const [busy, setBusy] = useState(false)

    const [invalidEntryOpen, setInvalidEntryOpen] = useState(false)

    const testOverlapTime = (alarm, modifying=false) => {
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
            if (alarmRepeatDays === 0) { // not the same day or both not repeating
                continue
            }
            const entryStart = moment(entry.time, "HH:mm") 
            const entryEnd = moment(entryStart).add(entry.alarmDuration, 'minutes')
            if ( 
                (alarmStart.isBetween(entryStart, entryEnd, 'minutes', '[)') || alarmEnd.isBetween(entryStart, entryEnd, 'minutes', '(]')) || 
                (alarmStart.isBefore(entryStart)  && alarmEnd.isAfter(entryEnd))) {
                return true  // there is an overlap
            }
        }
        return false
    } 
    
 
    useEffect(() => {
        const timer = setInterval(() => {
          if (busy) return
          onSync()
          
        }, 10000)
        return () => clearInterval(timer)
    }, [])

    const addAlarm = (newAlarm)  => {
        // test here for an overlapping alarm
        // if valid, add it
        //if not, put up a warning and ignore
        if (testOverlapTime(newAlarm)) {
            setInvalidEntryOpen(true)
        } else {
            dispatch({type: ACTIONS.ALARM_ADD, payload: newAlarm})
            asyncDispatch()
            setWorkingAlarm({})
        }
    }



    const updateAlarmList = (targetAlarm, shouldDelete)  => {
        const alarmID = targetAlarm.id
        if (shouldDelete) {  
            // confirm the item pointed to by teh index matched the date 
            dispatch({type: ACTIONS.ALARM_DELETE, payload: alarmID})
        } else { // update
            // check to see if the changes don;t cause a conflict
            if (testOverlapTime(workingAlarm, true)) {
                setInvalidEntryOpen(true)
            } else {
                dispatch({type: ACTIONS.ALARM_UPDATE, payload: targetAlarm})
            }
        }
        asyncDispatch()
        
        
        // TODO: update the redis object here
    }

    return(
        // a new alarm box
        // list of current
      
        <Stack direction="column"
            spacing={{sx:2, sm: 3, md:5}}
        >
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
                        addAlarm={addAlarm} dispatch={dispatch} setBusy={setBusy}
                    />
                </AccordionDetails>
            </Accordion>
            
         
            {listLoading ? <h4>Alarms Loading.....</h4> :
            <AlarmList alarmList={alarmList} updateAlarmList={updateAlarmList} setBusy={setBusy}/> }

            <InvalidAlarmEntry open={invalidEntryOpen} setOpen={setInvalidEntryOpen} />
            <h1>  </h1>
            
        </Stack>
     
    )
}

export default Alarm