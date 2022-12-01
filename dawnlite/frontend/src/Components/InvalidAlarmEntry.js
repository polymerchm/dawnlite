import React from 'react'
// import { useState } from 'react'
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });




const InvalidAlarmEntry = (props) => {
    const open = props.open
    const setOpen = props.setOpen
    //const postCloseAction = props.postCloseAction

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
          return;
        }
    
        setOpen(false);
        //postCloseAction()
    }

    return (
        <Snackbar open={open} autoHideDuration={6000} onClose={handleClose} anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}>
          <Alert onClose={handleClose} severity="error">Invalid time (overlapping)</Alert>
        </Snackbar>
    )

}

export default InvalidAlarmEntry