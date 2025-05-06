from bigbang.ingress import W3CMailList

# urls = W3CMailList.get_message_urls(
#   name="public-testtwf",
#    url="https://lists.w3.org/Archives/Public/public-testtwf/",
#    select={"years": 2014, "fields": "total"},
# )

# import pdb; pdb.set_trace()

mlist = W3CMailList.from_url(
    name="public-testtwf",
    url="https://lists.w3.org/Archives/Public/public-testtwf/",
    select={"years": 2014, "fields": "total"},
)


mlist.to_mbox("archives/public-testtwf.mbox")
