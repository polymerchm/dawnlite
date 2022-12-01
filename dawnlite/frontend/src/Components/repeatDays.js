import { Grid, FormControlLabel, Checkbox} from '@mui/material'

export const repeatDayData = [
    {bit: 1, name: "SU"},
    {bit: 2, name: "MO"},
    {bit: 4, name: "TU"},
    {bit: 8, name: "WE"},
    {bit: 16, name: "TH"},
    {bit: 32, name: "FR"},
    {bit: 64, name: "SA"}
]



export const repeatDaysControl = (props) => {
    return (
        <Grid container direction={"row"} columns={11} columnSpacing={5}>
        <Grid item xs={0} sm={2}/>
        {repeatDaysControl.map((alarm,index) =>  (                          
            <Grid item sm={1} key={index}>
                <FormControlLabel  control={<Checkbox />}
                label = {alarm.name}
                labelPlacement="top"
                    onChange={
                        props.changeRepeatDay(alarm)
                    }
                    />
            </Grid>
            ))
        }  
        <Grid item xs={0} sm={2}/>                 
        </Grid>
   )
}
