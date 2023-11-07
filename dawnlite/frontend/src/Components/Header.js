import React from 'react'

import {useEffect} from 'react'
import {AppBar, 
        Toolbar,
        Typography, 
        IconButton,
        Box
} from '@mui/material'
import RecycleIcon from '@mui/icons-material/Refresh'


const Header = ({level, nextAlarm}) => {


    return (
        <div>
            <AppBar position="static">
                <Toolbar>
                    <Box display='flex' flexGrow={1}>
                        <Typography variant="h6" component="div" color={level === 0 ? 'white' : 'yellow'} 
                        >Dawnlight</Typography>
                    </Box>
                    <Box display='flex' flexGrow={1}>
                        <Typography variant="h6" component="div" 
                        >{nextAlarm}</Typography>
                    </Box>
                    <IconButton 
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="refresh alarms"
                        sx={{ mr: 2 }}
                    > <RecycleIcon/>
                    </IconButton>
                </Toolbar>
            </AppBar>

        </div>
        )
    }

export default Header
