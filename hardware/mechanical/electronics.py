"""SI electronics mounting geometry and independent thread-stack arithmetic."""
def values(records):return {k:r['value'] for k,r in records.items()}
def calculate(data):
    p=values(data['electronics_mount']);m=values(data['mechanical'])
    x,y,z=p['tray_origin'];w,t,depth=p['tray_size'];h=p['spacer_length'];wh=p['washer_thickness']
    board=[x+(w-p['pcb_width'])/2,y+t+h,z+(depth-p['pcb_depth'])/2]
    support=[(x+dx,z+dz) for dx in (p['support_inset'],w-p['support_inset']) for dz in (p['support_inset'],depth-p['support_inset'])]
    board_holes=[(board[0]+p['pcb_width']/2+sx*p['pcb_pitch_x']/2,board[2]+p['pcb_depth']/2+sz*p['pcb_pitch_z']/2) for sx in (-1,1) for sz in (-1,1)]
    engagement=dict(floor_bottom=p['floor_screw_length']-m['wall']-wh,
        floor_top=p['small_screw_length']-t-wh,
        board_bottom=p['small_screw_length']-t-wh,
        board_top=p['small_screw_length']-p['pcb_thickness']-wh)
    gaps=dict(floor_pair=h-engagement['floor_bottom']-engagement['floor_top'],
        board_pair=h-engagement['board_bottom']-engagement['board_top'])
    return dict(tray_origin_m=p['tray_origin'],tray_size_m=p['tray_size'],board_origin_m=board,
        support_centres_m=support,pcb_hole_centres_m=board_holes,thread_engagement_m=engagement,screw_tip_gap_m=gaps,
        hole_pattern_tolerance_capacity_m=(p['tray_pcb_bore']-p['screw_diameter'])/2+(p['pcb_hole']-p['screw_diameter'])/2,
        status='nominal_mounting_design_no_board_keepout_or_thermal_release')
