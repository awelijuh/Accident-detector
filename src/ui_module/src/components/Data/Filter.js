import {
    Box,
    Chip,
    FormControl,
    IconButton,
    InputLabel,
    MenuItem,
    OutlinedInput,
    Select,
    TextField
} from "@mui/material";
import {Refresh} from "@mui/icons-material";
import {useEffect, useState} from "react";
import {DATA_URL} from "../../const";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};


export default function Filter(props) {
    let {onChange, value, onUpdate} = props

    const [classes, setClasses] = useState([])

    async function fetchClasses() {
        let resp = await fetch(DATA_URL + 'classes')
        if (!resp.ok) {
            return
        }
        let d = await resp.json()
        setClasses(d?.map?.(e => e.class_name))
    }

    useEffect(() => {
        fetchClasses()
    }, [props])

    return (
        <div className="d-flex">
            <TextField
                className="m-2"
                label="С"
                type="datetime-local"
                defaultValue={value?.start_time}
                sx={{width: 250}}
                InputLabelProps={{
                    shrink: true,
                }}
                onBlur={(e) => onChange?.({...value, start_time: e.target.value})}
            />
            <TextField
                className="m-2"
                label="До"
                type="datetime-local"
                defaultValue={value?.end_time}
                sx={{width: 250}}
                InputLabelProps={{
                    shrink: true,
                }}
                onBlur={(e) => onChange?.({...value, end_time: e.target.value})}
            />

            <FormControl className="m-2" variant="standard" sx={{m: 1, minWidth: 120}}>
                <InputLabel id="demo-simple-select-label" className="ms-2">Классы</InputLabel>
                <Select
                    multiple={true}
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={value?.classes}
                    label="Классы"
                    variant="standard"
                    sx={{width: 250}}
                    onChange={(e) => onChange?.({...value, classes: e.target.value})}
                    input={<OutlinedInput id="demo-simple-select" label="Chip"/>}
                    renderValue={(selected) => (
                        <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 0.5}}>
                            {selected?.map?.((value) => (
                                <Chip key={value} label={value}/>
                            ))}
                        </Box>
                    )}
                    MenuProps={MenuProps}
                >
                    {
                        classes?.map(e => <MenuItem key={e} value={e}>{e}</MenuItem>)
                    }
                </Select>

            </FormControl>

            <div className="ms-auto mt-auto mb-auto">
                <IconButton onClick={() => onUpdate?.()}>
                    <Refresh/>
                </IconButton>
            </div>
        </div>

    )
}
