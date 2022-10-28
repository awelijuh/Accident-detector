import React, {useEffect, useState} from "react";
import {DATA_URL} from "../../const";
import {FormControl, InputLabel, MenuItem, Select} from "@mui/material";

// import {FormControl, InputLabel, MenuItem, Select} from "@material-ui/core";


export function Info(props) {
    let options = props.options
    let onChangeOptions = props.onChangeOptions

    return (
        <div className="w-auto">
            <div className={"border p-2 w-auto"} style={{display: 'grid'}}>
                <FormControl className="m-2 w-auto" variant="standard">
                    <InputLabel id="type-label">Тип</InputLabel>
                    <Select
                        labelId="type-label"
                        id="type-select"
                        value={options?.type}
                        label="Тип"
                        variant="standard"
                        sx={{width: 300}}
                        onChange={(e) => onChangeOptions?.({...options, type: e.target.value})}
                    >
                        <MenuItem value={"raw"}>raw</MenuItem>
                        <MenuItem value={"detected"}>detected</MenuItem>
                    </Select>
                </FormControl>
                <FormControl className="m-2 w-auto" variant="standard" sx={{m: 1, minWidth: 120}}>

                    <InputLabel id="size-label">Размер</InputLabel>
                    <Select
                        labelId="size-label"
                        id="size-select"
                        value={options?.size}
                        label="Размер"
                        variant="standard"
                        sx={{width: 300}}
                        onChange={(e) => onChangeOptions?.({...options, size: e.target.value})}
                    >
                        <MenuItem value={"720"}>720p</MenuItem>
                        <MenuItem value={"540"}>540p</MenuItem>
                        <MenuItem value={"480"}>480p</MenuItem>
                        <MenuItem value={"360"}>360p</MenuItem>
                    </Select>
                </FormControl>
            </div>

        </div>
    )
}
