import React from 'react'

import {useEffect} from 'react'
import {AppBar, 
        Toolbar,
        Typography, 
        IconButton,
        Box
} from '@mui/material'
import RecycleIcon from '@mui/icons-material/Refresh'

import plugged from '../assets/plugged_white.png'
import unplugged from '../assets/unplugged_white.png'
import moment from 'moment'


const Header = ({level, nextAlarm, connected}) => {
    let connectionImage = connected ? plugged : unplugged
    return (
        <div>
            <AppBar position="static">
                <Toolbar>
                    <Box display='flex' flexGrow={1}>
                        <Typography variant="h6" component="div" color={level === 0 ? 'lightgray' : 'yellow'} 
                        >Dawnlight</Typography>
                    </Box>
                    <Box display='flex' flexGrow={1}>
                        <Typography variant="h6" component="div" 
                        >{moment(nextAlarm).year() > 1970 ? `next alarm - ${moment(nextAlarm).format("ddd, MMM D h:mma"

                        )}` : 'No Alarms Set'}</Typography>
                    </Box>
                    <Box component="img"
                            sx={{
                                height: 40,
                                width: 40,
                                maxHeight: { xs:30, md: 40 },
                                maxWidth: { xs: 30, md: 40 },
                                
                            }} src={connectionImage}/>
                    {/* <IconButton 
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="refresh alarms"
                        sx={{ mr: 2 }}
                    > <RecycleIcon/>
                    </IconButton> */}
                </Toolbar>
            </AppBar>
        </div>
        )
    }

export default Header
