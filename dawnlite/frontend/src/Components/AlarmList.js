import {
    List, ListItem,
} from '@mui/material'
import React from 'react'
import AlarmListItem from './AlarmListItem'



const AlarmList = ({alarmList, updateAlarmList}) => {
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
                            />
                        </ListItem>
                    ))
                }
            </List>  
        )
}

export default React.memo(AlarmList)