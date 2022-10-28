import React, {useEffect, useState} from "react";
import {Button, Container, Modal, Table} from "react-bootstrap-v5";
import moment from "moment";
import {DATA_URL, VIDEO_PREFIX} from "../const";
import {Info} from "./Stream/Info";

function VideoShower({show, url, onClose, name}) {
    console.log(url)
    return (
        <Modal show={show} onHide={() => onClose?.()} size="xl">
            <Modal.Header closeButton>
                <Modal.Title>{name}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <video className="ms-auto me-auto w-100" style={{maxHeight: 'calc(100vh - 70px)'}} controls src={url}/>
            </Modal.Body>
        </Modal>
    )
}

export function VideoTable(props) {

    const [data, setData] = useState()

    const [video, setVideo] = useState({show: false, url: null})

    async function fetchData() {
        let resp = await fetch(DATA_URL + 'accidents')
        if (!resp.ok) {
            return
        }
        let d = await resp.json()
        setData(d)
    }

    useEffect(() => {
        fetchData()
    }, [props])

    return (
        <Container>

            <Table bordered hover>
                <thead>
                <tr className="fw-bold">
                    <td>Время</td>
                    <td>Имя файла</td>
                    <td>Действие</td>
                </tr>
                </thead>
                <tbody>
                {
                    data?.map?.((value, index) => (
                        <tr key={index}>
                            <td className="fw-bolder">{value.time != null ? moment(value.time * 1000).format("DD.MM.YYYY HH:mm:ss.SSS") : ""}</td>
                            <td>{value.filename}</td>
                            <td>
                                <Button onClick={() => setVideo({
                                    show: true,
                                    video: VIDEO_PREFIX + value?.path,
                                    name: value?.filename
                                })}>Смотреть</Button>
                            </td>
                        </tr>
                    ))
                }

                </tbody>
            </Table>
            <VideoShower show={video?.show}
                         name={video?.name}
                         url={video?.video}
                         onClose={() => {setVideo({show: false})}}
            />

        </Container>

    )
}

