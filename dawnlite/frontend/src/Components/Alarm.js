import  { Stack, Button, Box }  from '@mui/material'
import AlarmEntry from './AlarmEntry'
import AlarmList from './AlarmList'

import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
//import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {useState} from 'react'



const Alarm = () => {

    
    const [alarmState, setAlarmState] = useState(false)

    const alarmStateSet = () => {
        setAlarmState(false)
    }

    return(
        // a new alarm box
        // list of current
        <Stack direction="column"
            spacing={{sx:2, sm: 3, md:5}}
        >
           <Accordion expanded={alarmState}>
                <AccordionSummary
                    // expandIcon={<ExpandMoreIcon />}
                    aria-controls="panel1a-content"
                    id="panel1a-header"
                >
                {alarmState ? null : <Box m="auto" ><Button onClick={()=> setAlarmState(true)}>New Alarm</Button></Box> }
                </AccordionSummary>
                <AccordionDetails>
                    <AlarmEntry  setAlarmState={setAlarmState}/>
                </AccordionDetails>
            </Accordion>
         
            <AlarmList/> 
            <h1>  </h1>
            
        </Stack>
    )
}

export default Alarm