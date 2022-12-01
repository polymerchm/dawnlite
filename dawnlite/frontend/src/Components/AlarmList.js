import {
    List, ListItem,
} from '@mui/material'

import AlarmListItem from './AlarmListItem'



const AlarmList = ({alarmList, setBusy, updateAlarmList}) => {
        return(  alarmList.length === 0 ? null : 
            <List>
                {
                    (alarmList.map((entry, index) => 
                       <ListItem key={index}>
                            <AlarmListItem 
                                itemIndex={index} 
                                isList={true}
                                alarmListItem={entry}
                                updateAlarmList={updateAlarmList}
                                setBusy={setBusy}
                            />
                        </ListItem>
                    ))
                }
            </List>  
        )
}

export default AlarmList