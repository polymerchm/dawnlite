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
    Switch, 
    FormGroup, 

    
} from '@mui/material'


import FormControlLabel from '@mui/material/FormControlLabel';
import TimePicker from 'rc-time-picker';
import 'rc-time-picker/assets/index.css';
import moment from 'moment'
import  { repeatDayData  } from './repeatDays' 
import getAlarm from './getAlarms'

const AlarmListItem = (props) => {
    const updateAlarmList=props.updateObjects
    const itemIndex = props.itemIndex
    const setAlarmState = props.setAlarmState
    const isList = props.isList

    const defaultAlarmObject = {date: '2021-12-31 01:01:01', alarmTime: '08:00', repeat: 0, duration: 20, intensity: 25, id: ''}
 
    const [alarmObject, setAlarmObject] = useState(isList ? props.alarmObject :  defaultAlarmObject)
         
    const [modify, setModify] = useState(false) 

    const changeRepeatDay = (bit) => (e) => {
        console.log(alarmObject, bit)
        setAlarmObject({...alarmObject, repeat: alarmObject.repeat ^ bit})    
    }

    const onTimeChanged =  (value)  => {
        setAlarmObject({...alarmObject, alarmTime: value.format('HH:mm')})
    }

    const onDurationChange = (e) => {
        setAlarmObject({...alarmObject, duration: e.target.value})
    }

    const onIntensityChange = (e) => {
        setAlarmObject({...alarmObject, intensity: e.target.value})
    }

    const onSave = (e)  => {
  
        //look for a similar alarm
        // if redundant, warn
        // if not, save it.
        // and force an update.
        setAlarmState(false)
        setAlarmObject(defaultAlarmObject)

    }


    const onCancel = (e) => {
        setAlarmObject(defaultAlarmObject)
        setAlarmState(false)
    }
  


    const ListButtons = () => { 
        const Buttons = () => {
            return ['a','b'].map(function(id,index){
                const onclicks = modify ?
                    { a: ()=> {setModify(false); updateAlarmList(alarmObject,itemIndex,false)}, 
                      b: () => {setModify(false); updateAlarmList(alarmObject,itemIndex, true)}
                    } 
                    : { a: onSave, b: onCancel } 
                const labels = modify ? { a: "Update", b: "Delete"} : { a: "Save", b: "Cancel"}
                return <Button size="medium"  
                    key={id}
                    variant="contained"
                    onClick={onclicks[id]} 
                    sx={{margin: '20px'}}>{labels[id]}
                </Button>
        })}
        if (!isList || (isList && modify)) {
            return (
                <Box m="auto" spacing={2}>
                    <Buttons/>
                </Box>    
            )
        } else {
            return null
        }
    }

    const CheckBoxEntry = (local) => {
        const name = local.repeatDay.name
        const bit = local.repeatDay.bit
            return (
                <FormControlLabel  control={<Checkbox 
                    checked={(bit & alarmObject.repeat) !== 0} 
                    disabled={isList && !modify}/>}
                    label = {name}
                    labelPlacement="top"
                    onChange={
                        changeRepeatDay(bit)
                    }/>)
        
    }
  
    return (
    <Card>
        <CardContent>
           
        {props.isList && 
 
                <FormGroup>
                    <FormControlLabel 
                    labelPlacement='start' 
                    control={<Switch  
                                checked={modify}  
                                onChange={(() => setModify(!modify))}/>} 
                    label="Edit" />
                </FormGroup>

        }  
            <Grid container>
                <Grid item xs={5}/>
                <Grid item xs={2}>
                <TimePicker 
                     
                    disabled={isList && !modify}
                    showSecond={false} 
                    use12Hours 
                    minuteStep={15} 
                    placeholder={'choose time'} 
                    value={moment(alarmObject.alarmTime, "hh:mm")}
                    onChange={onTimeChanged}
            />
            </Grid>
            <Grid item xs={5}/>
            </Grid>

            <Box m={2} >
                <Typography align='center' variant={"h5"}>Repeat</Typography>
            </Box>
            <Grid container direction={"row"} columns={11} columnSpacing={5}>
                <Grid item xs={0} sm={2}/>
                {repeatDayData.map((repeatDay, index) => (                          
                            <Grid item sm={1} key={repeatDay.bit}>    
                                <CheckBoxEntry repeatDay={repeatDay} /> 
                            </Grid>
                            ))
                        } 
                <Grid item xs={0} sm={2}/>                 
            </Grid>
            <Grid container >
                <Grid item xs={3}/>
                <Grid item xs={2}>
                    <InputLabel >Duration</InputLabel>
                    <Select
                        id="durationSelect"
                        value={alarmObject.duration}
                        disabled = {isList && !modify}
                        onChange={onDurationChange}
                    >
                        <MenuItem value={20}>20 Minutes</MenuItem>
                        <MenuItem value={45}>45 Minutes</MenuItem>
                        <MenuItem value={60}>1 hour</MenuItem>
                        <MenuItem value={120}>2 hours</MenuItem>
                    </Select> 
                </Grid>
                <Grid item xs={2}/>
                <Grid item xs={2}>
                    <InputLabel >Intensity</InputLabel>
                    <Select
                        id="intensitySelect"
                        value={alarmObject.intensity}
                        onChange={onIntensityChange}
                        disabled = {isList && !modify}
                    >
                        <MenuItem value={25}>25%</MenuItem>
                        <MenuItem value={50}>50%</MenuItem>
                        <MenuItem value={75}>75%</MenuItem>
                        <MenuItem value={100}>100%</MenuItem>
                    </Select> 
                </Grid>
                <Grid item xs={3}/>
            </Grid>
        </CardContent>
        <CardActions>
            <ListButtons />
        </CardActions>  
    </Card>
    )
   
}

export default AlarmListItem
