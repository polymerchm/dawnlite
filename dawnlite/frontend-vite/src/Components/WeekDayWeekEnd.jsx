import React from 'react'
import {  Button, 
          ButtonGroup 
        } from '@mui/material'

const WeekDayWeekEnd = ({setRepeatDays,repeatDays,visible}) => {

  const onClick = (e) => {
    switch (e.target.id) {
      case "clear":
        setRepeatDays(0)
        break;
        case "daily":
          setRepeatDays(0b1111111)  
          break 
        case "weekends":
          setRepeatDays(0b1000001) 
          break    
        case "weekdays":
          setRepeatDays(0b0111110)
        break
    
      default:
        break;
    }
  }

  return ( visible ? 
    <ButtonGroup variant="contained" sx={{ml: 'auto', mr: 'auto', mt: 3, mb: 3}}>
      <Button id='clear' onClick={onClick}>Clear All</Button>
      <Button id='daily' onClick={onClick}>Daily</Button>
      <Button id='weekdays' onClick={onClick}>Weekdays</Button>
      <Button id='weekends' onClick={onClick}>Weekends</Button>
    </ButtonGroup>
    : null
  )
}

export default WeekDayWeekEnd