import {
    useState,
} from 'react'
import {
    List, ListItem,
} from '@mui/material'


import getAlarms from './getAlarms'
import AlarmListItem from './AlarmListItem'



const AlarmList = () => {
const [alarmObjects, setAlarmsObjects] = useState(getAlarms())

const updateAlarmList = (alarmObject, itemIndex, willDelete) => {
    const objects = [...alarmObjects]
    if (willDelete) {
        const alarmDate = alarmObject.date
        // confirm the item pointed to by teh index matched the date
        const selectedObject = alarmObjects[itemIndex]
        if (selectedObject.date !== alarmDate) {
            console.log("did not match", selectedObject.date, alarmDate)
        } else {
            objects.splice(itemIndex,1) 
        }
    } else { // update
        objects[itemIndex] = alarmObject
    }
    setAlarmsObjects(objects)
    // update the redis object here
}



    return(  
        <List>
            {
                (alarmObjects.map((alarmObject, index) => 
                    <ListItem key={index}>
                        <AlarmListItem 
                            alarmObject={alarmObject} 
                            updateObjects={updateAlarmList} 
                            itemIndex={index} 
                            isList={true}/>
                    </ListItem>
                ))
            }
        </List>  
    )
}

export default AlarmList