import moment from "moment";

export function getDateFormatFromFileName(filename) {
    let name = filename.toString().replace(".jpg", "")

    let date = new Date(parseFloat(name) * 1000)

    return moment(date).format("DD.MM.YYYY HH:mm:ss")
}
