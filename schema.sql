drop table if exists label_set;
create table label_set(
  id integer primary key autoincrement,
  video_path string not null,
  video_name string not null,
  arousal_level integer not null,
  excitement_level integer not null,
  pleasure_level integer not null,
  contentment_level integer not null,
  sleepiness_level integer not null,
  depression_level integer not null,
  misery_level integer not null,
  distress_level integer not null
);

create index root_index on label_set (video_path);