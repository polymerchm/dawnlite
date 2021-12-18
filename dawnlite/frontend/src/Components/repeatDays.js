import { Grid, FormControlLabel, Checkbox} from '@mui/material'

export const repeatDayData = [
    {bit: 1, name: "Sun"},
    {bit: 2, name: "Mon"},
    {bit: 4, name: "Tue"},
    {bit: 8, name: "Wed"},
    {bit: 16, name: "Thu"},
    {bit: 32, name: "Fri"},
    {bit: 64, name: "Sat"}
]

// export const getRepeatData = (index) => {
//     return repeatDayData[index]

// }

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
