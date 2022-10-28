import React, {useEffect, useState} from "react";
import {DATA_URL} from "../../const";
import {FormControl, InputLabel, MenuItem, Select} from "@mui/material";

function Item({name, value}) {
    return (
        <tr>
            <td className="fw-bold" style={{width: '200px'}}>{name}:</td>
            <td className="text-end">{value}</td>
        </tr>
    )
}


export function Benchmarks(props) {
    const [params, setParams] = useState();
    let options = props.options
    let onChangeOptions = props.onChangeOptions

    async function fetchBenchmarks() {
        let resp = await fetch(DATA_URL + "benchmark")
        if (resp.ok) {
            let f = await resp.json()
            setParams(f)
        }
    }

    useEffect(() => {
        const interval = setInterval(() => {
            fetchBenchmarks()
        }, 5000);
        return () => clearInterval(interval);
    }, [props]);

    return (
        <div className="w-auto me-2">
            <div className="border p-2" style={{display: 'grid'}}>
                <table>
                    <tbody>
                    <Item name="read fps" value={params?.read_fps?.toFixed?.(3)}/>
                    <Item name="detect fps" value={params?.detect_fps?.toFixed?.(3)}/>
                    <Item name="yolo time" value={params?.yolo_time?.toFixed?.(3)}/>
                    <Item name="track time" value={params?.tracker_time?.toFixed?.(3)}/>
                    <Item name="Запись" value={params?.is_saving === true ? "on" : "off"}/>
                    </tbody>
                </table>
            </div>

        </div>
    )
}
