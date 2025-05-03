-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_transit_stops_populates_fields_on_new_record after insert on Transit_Stops
begin
    update Transit_Stops
    set "x" = round(ST_X(new.geo), 8),
    "y" = round(ST_Y(new.geo), 8)
    where Transit_Stops.rowid = new.rowid;

    INSERT INTO editing_table VALUES(NULL, 'Transit_Stops', 'stop',new.stop_id, NULL, NULL, 'ADD', 0, '');
end;

--##
create trigger if not exists polaris_transit_stops_on_x_change after update of "x" on Transit_Stops
begin
    update Transit_Stops
    set "x" = round(ST_X(new.geo), 8)
    where Transit_Stops.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_stops_on_y_change after update of "y" on Transit_Stops
begin
    update Transit_Stops
    set "y" = round(ST_Y(new.geo), 8)
    where Transit_Stops.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_transit_stops_on_zone_change after update of "zone" on Transit_Stops
begin
    INSERT INTO editing_table VALUES(NULL, 'Transit_Stops', 'stop', new.stop_id, 'zone', NULL, 'EDIT', 0, '');
end;

--##
create trigger if not exists polaris_transit_stops_on_geo_change after update of geo on Transit_Stops
begin
    update Transit_Stops
    set "x" = round(ST_X(new.geo), 8),
    "y" = round(ST_Y(new.geo), 8)
    where Transit_Stops.rowid = new.rowid;

    update Transit_Walk
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.stop_id
    and StartPoint(geo) != new.geo;

    update Transit_Walk
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.stop_id
    and EndPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetStartPoint(geo,new.geo)
    where from_node = new.stop_id
    and StartPoint(geo) != new.geo;

    update Transit_Bike
    set geo = SetEndPoint(geo,new.geo)
    where to_node = new.stop_id
    and EndPoint(geo) != new.geo;

    INSERT INTO editing_table VALUES(NULL, 'Transit_Stops', 'stop',new.stop_id, 'geo', NULL, 'EDIT', 0, '');
end;

--##
create trigger if not exists polaris_transit_stops_on_delete_record_block_if_in_use before delete on Transit_Stops
  when (select sum(c) from (SELECT count(*) c FROM Transit_Pattern_Mapping WHERE stop_id = old.stop_id
  union all SELECT count(*) c FROM Transit_Links WHERE from_node = old.stop_id
  union all SELECT count(*) c FROM Transit_Links WHERE to_node = old.stop_id
  union all SELECT count(*) c FROM Transit_Walk WHERE from_node = old.stop_id
  union all SELECT count(*) c FROM Transit_Walk WHERE to_node = old.stop_id
  union all SELECT count(*) c FROM Transit_Bike WHERE from_node = old.stop_id
  union all SELECT count(*) c FROM Transit_Bike WHERE to_node = old.stop_id))>0

  BEGIN
    SELECT raise(ABORT, 'Stop cannot be deleted, it is apparently still needed.');
  END;
