import json

result = []

for i in range(20200920, 20201106):
  if i == 20200926 and i == 20200927 and i == 20200930 and i == 20201001 and i == 20201002 and i == 20201003 and i == 20201004 and i == 20201009 and i == 20201010 and i == 20201011 and i == 20201017 and i == 20201018 and i == 20201024 and i == 20201025 and i == 20201101 and i == 20201102:
    pass
  elif i == 20201027:
    result.append({
      "date": i,
      "grade": "3학년"
    })
  elif i == 20201102:
    result.append({
      "date": i,
      "grade": "2학년 3학년"
    })
  elif i < 20200926:
    result.append({
      "date": i,
      "grade": "2학년 3학년"
    })
  elif i < 20200929:
    result.append({
      "date": i,
      "grade": "1학년 3학년"
    })
  else:
    result.append({
      "date": i,
      "grade": "1학년 2학년"
    })

with open("going_school.json", "w") as f:
  json.dump(result, f)