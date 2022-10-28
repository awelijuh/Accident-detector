import {Container} from "react-bootstrap-v5";
import React, {useEffect, useState} from "react";
import {Info} from "./Info";
import {Benchmarks} from "../Benchmark/BenchmarkMini";
import {DATA_URL} from "../../const";


export function VideoView(props) {
    const [options, setOptions] = useState({size: '480', type: 'detected'})

    return (
        <div className="d-flex">
            <img className="ms-1 me-1" style={{maxHeight: 'calc(100vh - 70px)'}} src={DATA_URL + "stream?type=" + options?.type + "&size=" + options?.size}/>
            <div className="ms-auto w-auto">
                <Info options={options} onChangeOptions={setOptions}/>
                <Benchmarks/>
            </div>
        </div>
    )
}
