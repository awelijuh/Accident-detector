import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from redis import Redis
from sqlalchemy import and_, func, extract
from sqlalchemy.orm import Session, joinedload

from database_module import db_models
from database_module import redis_constants
from database_module.db import engine, SessionLocal
from database_module.redis_db import get_redis_db

db_models.Base.metadata.create_all(bind=engine)


def create_frame(time, boxes):
    db: Session = SessionLocal()

    frame = db_models.Frame(time=datetime.fromtimestamp(time))
    db.add(frame)

    for b in boxes:
        bx = db_models.Box(**b, frame=frame)
        db.add(bx)
    db.commit()
    db.flush()
    db.close()


def get_p_from_scale(scale):
    p = {
        'second': 1,
        'minute': 1 * 60,
        'hour': 1 * 60 * 60,
        'day': 1 * 60 * 60 * 24,
        'week': 1 * 60 * 60 * 24 * 7,
    }
    return p.get(scale, 1)


def get_method_from_aggregate(aggregate):
    p = {
        'max': max,
        'min': min,
        # 'average': average,
        # 'median': median,
    }
    return p.get(aggregate, max)


def get_func_by_aggregate(aggregate):
    p = {
        'max': func.max,
        'min': func.min,
        # 'average': func.avg,
        # 'median': func.median,
    }
    return p.get(aggregate, func.max)


@dataclass
class BoxFrame:
    time: datetime
    class_name: str
    count: int


def get_group_by_scale(scale, time):
    result = []
    result.append(extract('year', time))
    result.append(extract('month', time))
    result.append(extract('week', time))
    if scale == 'week':
        return result
    result.append(extract('day', time))
    if scale == 'day':
        return result
    result.append(extract('hour', time))
    if scale == 'hour':
        return result
    result.append(extract('minute', time))
    if scale == 'minute':
        return result
    result.append(extract('second', time))
    if scale == 'second':
        return result
    return [time]


def filter_delta_time(start_time=None, end_time=None, classes=None):
    db: Session = SessionLocal()

    wh = []
    if start_time is not None:
        wh.append(db_models.Frame.time >= datetime.fromisoformat(start_time))
    if end_time is not None:
        wh.append(db_models.Frame.time < datetime.fromisoformat(end_time))
    if classes is not None and classes != '':
        cls = tuple(classes.split(','))
        wh.append(db_models.Box.class_name.in_(cls))
    query = db.query(((func.julianday(func.max(db_models.Frame.time)) - func.julianday(
        func.min(db_models.Frame.time))) * 24 * 60 * 60).label('delta'), db_models.Box.obj_id,
                     db_models.Box.class_name).select_from(db_models.Box).join(db_models.Frame) \
        .where(and_(*wh)).group_by(db_models.Box.obj_id).order_by('delta')

    print(query)

    result = list(query.all())
    db.close()

    return result


def get_all_class_names(start_time=None, end_time=None):
    db: Session = SessionLocal()

    c = db.query(db_models.Box.class_name).select_from(db_models.Box).distinct()
    result = list(c.all())
    db.close()

    return result


def get_frames_data2(start_time=None, end_time=None, scale=None, aggregate=None):
    db: Session = SessionLocal()

    wh = []
    if start_time is not None:
        wh.append(db_models.Frame.time >= datetime.fromisoformat(start_time))
    if end_time is not None:
        wh.append(db_models.Frame.time < datetime.fromisoformat(end_time))

    d_sub = db.query(func.min(db_models.Frame.time).label('time'), db_models.Box.class_name,
                     func.count(db_models.Box.class_name).label('count')) \
        .join(db_models.Box.frame).group_by(db_models.Frame.id, db_models.Box.class_name).where(and_(*wh)).subquery()
    frames = db.query(func.min(d_sub.c.time), d_sub.c.class_name,
                      get_func_by_aggregate(aggregate)(d_sub.c.count)).select_from(
        d_sub).group_by(*get_group_by_scale(scale, d_sub.c.time), d_sub.c.class_name)
    frames = frames.all()

    frames = [BoxFrame(*i) for i in frames]
    times = {}
    p = get_p_from_scale(scale)
    for i in frames:
        nt = datetime.fromtimestamp((i.time.timestamp() // p) * p)
        # nt = i.time
        if nt not in times:
            times[nt] = {'all': 0}
        times[nt]['time'] = nt
        times[nt][i.class_name] = i.count
        times[nt]['all'] += i.count
    frames = times.values()

    # if scale is not None and scale != '':
    #     p = get_p_from_scale(scale)
    #     r = {}
    #     for frame in frames:
    #         tt: datetime = frame['time']
    #         frame['time'] = datetime.fromtimestamp((tt.timestamp() // p) * p)
    #
    #         if frame['time'] not in r:
    #             r[frame['time']] = {}
    #         current = r[frame['time']]
    #         for key in frame:
    #             if key not in current:
    #                 current[key] = []
    #             current[key].append(frame[key])
    #
    #         # r[frame['time']].append(frame)
    #     method = get_method_from_aggregate(aggregate)
    #     for tt in r:
    #         for key in r[tt]:
    #             if key == 'time':
    #                 r[tt][key] = r[tt][key][0]
    #             else:
    #                 r[tt][key] = method(r[tt][key])
    #
    #     frames = r.values()

    result = list(frames)

    db.close()

    return result


def get_frames_data(start_time=None, end_time=None, scale=None, aggregate=None):
    db: Session = SessionLocal()

    wh = []

    if start_time is not None:
        print('start_time', start_time, datetime.fromisoformat(start_time))
        wh.append(db_models.Frame.time >= datetime.fromisoformat(start_time))
    if end_time is not None:
        print('end_time', end_time, datetime.fromisoformat(end_time))
        wh.append(db_models.Frame.time < datetime.fromisoformat(end_time))
    boxes = db.query(db_models.Box).options(joinedload(db_models.Box.frame, innerjoin=True)).join(
        db_models.Frame).where(
        and_(*wh)).all()

    frames = {}
    for b in boxes:
        frame_id = b.frame.id
        if frame_id not in frames:
            frames[frame_id] = {}
        frames[frame_id]['time'] = b.frame.time
        if b.class_name not in frames[frame_id]:
            frames[frame_id][b.class_name] = 0
        frames[frame_id][b.class_name] += 1
        if 'all' not in frames[frame_id]:
            frames[frame_id]['all'] = 0
        frames[frame_id]['all'] += 1

    frames = frames.values()

    if scale is not None and scale != '':
        p = get_p_from_scale(scale)
        r = {}
        for frame in frames:
            tt: datetime = frame['time']
            frame['time'] = datetime.fromtimestamp((tt.timestamp() // p) * p)

            if frame['time'] not in r:
                r[frame['time']] = {}
            current = r[frame['time']]
            for key in frame:
                if key not in current:
                    current[key] = []
                current[key].append(frame[key])

            # r[frame['time']].append(frame)
        method = get_method_from_aggregate(aggregate)
        for tt in r:
            for key in r[tt]:
                if key == 'time':
                    r[tt][key] = r[tt][key][0]
                else:
                    r[tt][key] = method(r[tt][key])

        frames = r.values()

    result = list(frames)

    db.close()

    return result


def get_all_boxes():
    db: Session = SessionLocal()
    return db.query(db_models.Box).join(db_models.Frame).all()


