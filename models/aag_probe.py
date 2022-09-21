import aag_api


#t =aag_api.get_tournament(213433)
#t =aag_api.get_enrolled(101261)
t = aag_api.get_tournaments()
print(t)
        
#r = aag_api.do_get("/fields")
#print(r.json())
#print(aag_api.get_handicap(48.0))
