import {  IconButton, 
          Stack,  
          Slider,
          Box
        } from '@mui/material'
import LightbulbOff from '@mui/icons-material/Nightlight';
import LightbulbOn from '@mui/icons-material/WbSunnyOutlined';
import { ACTIONS } from '../App'

// import {useState, useEffect} from 'react'
// import { debounce } from 'lodash'



const Light = ({dispatch, brightness}) => {

  



  

  const dispatchChange = (value) => {
    dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: value})
  }


  const  newIntensity =  (e,value) => {
    if ((e.type === "mousedown" || e.type === "mousemove") && value === 0) {
      dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: value})
    }
      
  }

  const commitedIntensity = (e,value) => {
    if (e.type === "mouseup") {
      dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: value})
    }
    if (e.type === "mousemove" && value === 0) {
      dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: value})
    }

  }

  


 

  const buttonStyle = { fontSize: 300 }
   

  const arrayOfIcons = [
    <LightbulbOff style={buttonStyle}/> , 
    <LightbulbOn style={buttonStyle}/>
    ]
  return(
      // on-off switch
      // if on, then a slider
      // 
    <Stack>
      <IconButton onClick={() => {
          if (brightness === 0) {
            dispatchChange(50)
          } else {
            dispatchChange(0)
          }
      }}>
      {arrayOfIcons[brightness === 0 ? 0 : 1]}
      </IconButton>
        <Box m={5}>
        { brightness !== 0   ? 
        <Slider
          // defaultValue={defaultValue}
          value={brightness}
          step={5}
          valueLabelDisplay="auto"
          marks={[
            {value: 0,    label: "off"}, 
            {value: 25,   label: "25%"},
            {value: 50,   label: "50%"},
            {value: 75,   label: "75%"},
            {value: 100,  label: "full"}
          ]}
          onChange={newIntensity}
          onChangeCommitted={commitedIntensity}
        /> 
  
          : null}
        </Box>
    </Stack>
    
  )
}

export default Light