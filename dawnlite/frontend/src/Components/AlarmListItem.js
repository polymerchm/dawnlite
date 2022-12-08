import React from 'react'
import { useState, useEffect , useRef} from 'react'
import {
    Card,
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
    FormGroup
} from '@mui/material'


import FormControlLabel from '@mui/material/FormControlLabel';
import TimePicker from 'rc-time-picker';
import 'rc-time-picker/assets/index.css';
import moment from 'moment'
import { repeatDayData } from './repeatDays'
import { defaultAlarm } from './getAlarms'
import { uuid } from '../uuid'
import WeekDayWeekEnd from './WeekDayWeekEnd';





const AlarmListItem = ({ isList,
    updateAlarmList,
    setCreateNewAlarmFlag,
    addAlarm,
    alarmListItem,
    }) => {
    const [workingAlarm, setWorkingAlarm] = useState({...alarmListItem})
    const [modify, setModify] = useState(false)
    const [isDirty, setIsDirty] = useState(false)
    const itemRef = useRef()

    useEffect(() => {
        if (alarmListItem !== undefined) {
            setWorkingAlarm({...alarmListItem})
        }
    }, [alarmListItem])

    useEffect(() => {
        if (modify) itemRef.current.scrollIntoView({alignToTop: false,  behavior: 'smooth'})
    },[modify])



    const changeRepeatDay = (bit) => (e) => {
        setIsDirty(true)
        setWorkingAlarm({ ...workingAlarm, repeatDays: workingAlarm.repeatDays ^ bit })
    }


    const onTimeChanged = (value) => {
        setIsDirty(true)
        setWorkingAlarm({ ...workingAlarm, time: value.format('HH:mm') })
    }

    const onDurationChange = (e) => {
        setIsDirty(true)
        setWorkingAlarm({ ...workingAlarm, alarmDuration: e.target.value })
    }

    const onIntensityChange = (e) => {
        setIsDirty(true)
        setWorkingAlarm({ ...workingAlarm, level: e.target.value })
    }

    const onEnabledChange = (e) => {
        //TODO: check here to make sure this does not create an overlap of active alarms
        setWorkingAlarm({ ...workingAlarm, enabled: e.target.checked })
    }

    const setRepeatDays = (mask) => {
        setIsDirty(true)
        setWorkingAlarm({ ...workingAlarm, repeatDays: mask })
    }

    const onSave = (e) => {
        addAlarm({ ...workingAlarm, id: uuid() })
        setWorkingAlarm(defaultAlarm())
        setCreateNewAlarmFlag(false)
    }

    const getTimeValue = () => {
        return workingAlarm.time ? moment(workingAlarm.time, "hh:mm") : moment().hour(0).minute(0)
    }

    const onCancel = (e) => {
        setWorkingAlarm(defaultAlarm())
        setCreateNewAlarmFlag(false)
    }

    const onClickModifyButtons = (willDelete) => {
        if (updateAlarmList(workingAlarm, willDelete)) {
            setIsDirty(false)
            setModify(false)
        } else {
            setWorkingAlarm({...alarmListItem})
        }
        
    }

    const onEditChange = (e) => {
        if (!e.target.checked) {
            if (isDirty) {
                setWorkingAlarm({...alarmListItem})
                setIsDirty(false)
            }
        } 
        setModify(e.target.checked)
       
    }



    const EditableListItem = () => {
        if (!isList || (isList && modify)) {
        return (
            <Box>
            <Grid container >
                    <Grid item xs={5} sx={{m: 1}}/>
                    <Grid item xs={2} p={2}>
                        <TimePicker
                            disabled={isList && !modify}
                            showSecond={false}
                            use12Hours
                            minuteStep={1}
                            placeholder={'choose time'}
                            value={getTimeValue()}
                            onChange={onTimeChanged}
                            allowEmpty={false}
                            focusOnOpen={true}                     
                        />
                    </Grid>
                    <Grid item xs={5} />
                </Grid>
   
                <Grid container direction={"row"} columns={11} columnSpacing={5}>
                    <Grid item xs={0} sm={2} />
                    {repeatDayData.map((repeatDay, index) => (
                        <Grid item sm={1} key={repeatDay.bit}>
                            <RepeatCheckBoxEntry repeatDay={repeatDay} />
                        </Grid>
                    ))
                    }
                    <Grid item xs={0} sm={2} />
                </Grid>

                <Grid container direction={"row"} columns={3} columnSpacing={5}>
                    <WeekDayWeekEnd
                        setRepeatDays={setRepeatDays}
                        repeatDays={workingAlarm.repeatDays}
                        visible={modify || !isList }
                    />
                </Grid>
                <Grid container >
                    <Grid item xs={3} />
                    <Grid item xs={2}>
                        <InputLabel >Duration</InputLabel>
                        <Select
                            id="durationSelect"
                            value={workingAlarm.alarmDuration || 60}
                            disabled={isList && !modify}
                            onChange={onDurationChange}
                        >
                            <MenuItem value={2}>2 Minutes</MenuItem>
                            <MenuItem value={20}>20 Minutes</MenuItem>
                            <MenuItem value={30}>30 Minutes</MenuItem>
                            <MenuItem value={45}>45 Minutes</MenuItem>
                            <MenuItem value={60}>1 hour</MenuItem>
                            <MenuItem value={120}>2 hours</MenuItem>
                        </Select>
                    </Grid>
                    <Grid item xs={2} />
                    <Grid item xs={2}>
                        <InputLabel >Intensity</InputLabel>
                        <Select
                            id="intensitySelect"
                            value={workingAlarm.level || 100}
                            onChange={onIntensityChange}
                            disabled={isList && !modify}
                        >
                            <MenuItem value={25}>25%</MenuItem>
                            <MenuItem value={50}>50%</MenuItem>
                            <MenuItem value={75}>75%</MenuItem>
                            <MenuItem value={100}>100%</MenuItem>
                        </Select>
                    </Grid>
                    <Grid item xs={3} />

     
                        <Box sx={{mt: 1, mb: 1}} m='auto'>
                        <FormControlLabel  control={<Switch 
                            disabled={isList && !modify} />}
                            label="Enabled"
                            labelPlacement="start"
                            checked={workingAlarm.enabled || false}
                            onChange={onEnabledChange}
                            
                        />
                        </Box>
                </Grid>
            </Box>
        ) 
        } else {
            return null
        }
        
    }


    const repeatToString = (bitmask) => {
        let out = ""
        let pointer = 1
        let days = ['Su','Mo','Tu','We','Th','Fr','Sa']
        for ( let i=0; i < days.length; i++) {
            let value = (bitmask & pointer) ? days[i] : '__'   
            out += value
            pointer *= 2
        }
        return out
    }

    const DisplayableListItem = () => {
        let days = ""
        switch (workingAlarm.repeatDays) {
            case 0b1111111:
                days = 'daily'
                break;
            case 0b1000001:
                days = 'weekends'
                break;
            case 0b0111110:
                days = 'weekdays'
                break;
            default:
                days = repeatToString(workingAlarm.repeatDays)
                break;
        }
        
        let time =  moment(workingAlarm.time, "hh:mm").format('h:mma')
        let level = `${workingAlarm.level}%`
        let duration = workingAlarm.alarmDuration < 60 ? `${workingAlarm.alarmDuration} minutes` : `${workingAlarm.alarmDuration /  60} hours`
        if (workingAlarm.alarmDuration === 60) {
            duration = duration.slice(0, -1)
        } 
        let enabled = workingAlarm.enabled ? "enabled" : "disabled"

        if (isList && !modify) {
        return (
            <Box m="auto" spacing={2}>
                <Grid container 
                    spacing={{xs: 1, sm: 4, md: 6}}   
                    alignItems="center"
                    justifyContent="center"
                >
                    <Grid item > <Typography variant='h6'>{days}</Typography> </Grid>
                    <Grid item > <Typography variant='h6'>{time}</Typography> </Grid>
                    <Grid item > <Typography variant='h6'>{duration}</Typography> </Grid>
                    <Grid item  > <Typography variant='h6'>{level}</Typography> </Grid>
                    <Grid item > <Typography variant='h6'>{enabled}</Typography> </Grid>
                </Grid>
            </Box>
        )
        }
        else {
            return null
        }
    }


    const ListItemButtons = () => {
        const Buttons = () => {
            // let ref = useRef()
            // useEffect(()=>{
            //     if (modify) {
            //         ref.current.scrollIntoView({behavior: 'smooth'})

            //     }
            // },[modify])
            return ['a', 'b'].map(function (id, index) {
                const onclicks = modify ?
                    {
                        a: () => { onClickModifyButtons(false) },
                        b: () => { onClickModifyButtons(true) }
                    }
                    : { a: onSave, b: onCancel }
                const labels = modify ? { a: "Update", b: "Delete" } : { a: "Save", b: "Cancel" }
                return <Button size="medium" // ref={ref}
                    key={id}
                    variant="contained"
                    onClick={onclicks[id]}
                    sx={{ margin: '20px' }}>{labels[id]}
                </Button>
            })
        }
        if (!isList || (isList && modify)) {
            return (
                <Box m="auto" spacing={2}>
                    <Buttons />
                </Box>
            )
        } else {
            return null
        }
    }

    const RepeatCheckBoxEntry = ({ repeatDay }) => {
        const name = repeatDay.name
        const bit = repeatDay.bit
        return (
            <FormControlLabel control={<Checkbox
                checked={(bit & workingAlarm.repeatDays) !== 0}
                disabled={isList && !modify} />}
                label={name}
                labelPlacement="top"
                onChange={
                    changeRepeatDay(bit)
                } />)
    }

    return (
    <Card sx={{ margin: 'auto' , mt: 0}}> 
        <CardContent ref={itemRef}>
            {isList &&
                <FormGroup>
                    <FormControlLabel
                        labelPlacement='start'
                        control={<Switch
                            checked={modify}
                            onChange={onEditChange} />}
                        label="Edit" />
                </FormGroup>
            }
            <EditableListItem />
            <DisplayableListItem />
        </CardContent>
        <CardActions>
            <ListItemButtons />
        </CardActions>
    </Card>)
}

const notChanged = (prevProps, newProps) => {
    return true
}

export default React.memo(AlarmListItem, notChanged)
