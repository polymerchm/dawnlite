import {  IconButton, 
          Stack,  
          Box
        } from '@mui/material'
import LightbulbOff from '@mui/icons-material/Nightlight';
import LightbulbOn from '@mui/icons-material/WbSunnyOutlined';
import { ACTIONS } from '../App'
import { useState, useEffect } from 'react';
import Slider from 'react-rangeslider'
import 'react-rangeslider/lib/index.css'

const Light = ({dispatch, brightness}) => {
  const [localBrightness, setLocalBrightness] = useState(brightness)

  useEffect(() => {
    setLocalBrightness(brightness)
  }, [brightness])

  const Change = (value) => {
    setLocalBrightness(value)
  }

  const ChangeComplete = () => {
    dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: localBrightness})
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
          if (localBrightness === 0) {
            setLocalBrightness(50)
            dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: 50})
          } else {
            setLocalBrightness(0)
            dispatch({type: ACTIONS.SET_LIGHT_BRIGHTNESS, payload: 0})
          }
      }}>
      {arrayOfIcons[localBrightness === 0 ? 0 : 1]}
      </IconButton>
        <Box m={5}>
        { localBrightness !== 0   ? 
    
        <Slider
          value={localBrightness}
          step={5}
          min={0}
            max={100}
            labels={
              {
                0: '0%',
                25: '25%',
                50: '50%',
                75: '75%',
                100: 'full'
              }
            }
            onChange={Change}
            onChangeComplete={ChangeComplete}
          />
  
          : null}
        </Box>
    </Stack>
    
  )
}

export default Light