workflow = {
	name = "workflow to do something",
	description = "blah blah blah",
	projects = {},
	contexts = {},
	tasks = {
			{
				task = "task0",
				checklist = {
					"check thing",
					"check another thing",
					"check yet another thing",
				},
				metrics = {
					metric1= "integer",
					metric2= "numeric"
				},
				next = "value or a lambda"
			}
		}
	}

for k, v in pairs(workflow) do
    print(k)
    print(v)
end
