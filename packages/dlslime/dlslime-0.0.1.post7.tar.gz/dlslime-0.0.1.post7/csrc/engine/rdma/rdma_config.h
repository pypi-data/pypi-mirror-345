#pragma once

#include "utils/json.hpp"
#include "utils/logging.h"

#include <cstdint>
#include <functional>
#include <infiniband/verbs.h>
#include <iostream>
#include <string>
#include <tuple>
#include <unordered_map>

namespace slime {

const static int MAX_SEND_WR = 8192;
const static int MAX_RECV_WR = 8192;
const static int POLL_COUNT = 256;

using json = nlohmann::json;

typedef struct rdma_info {
    uint32_t      qpn;
    union ibv_gid gid;
    int64_t       gidx;
    uint16_t      lid;
    uint64_t      psn;
    uint64_t      mtu;
    rdma_info() {}
    rdma_info(uint32_t qpn, union ibv_gid gid, int64_t gidx, uint16_t lid, uint64_t psn, uint64_t mtu):
        qpn(qpn), gidx(gidx), lid(lid), psn(psn), mtu(mtu), gid(gid)
    {
    }

    rdma_info(json json_config)
    {
        gid.global.subnet_prefix = json_config["gid"]["subnet_prefix"];
        gid.global.interface_id  = json_config["gid"]["interface_id"];
        gidx                     = json_config["gidx"];
        lid                      = json_config["lid"];
        qpn                      = json_config["qpn"];
        psn                      = json_config["psn"];
        mtu                      = json_config["mtu"];
    }

    json to_json() const
    {
        json gid_config{{"subnet_prefix", gid.global.subnet_prefix}, {"interface_id", gid.global.interface_id}};
        return json{{"gid", gid_config}, {"gidx", gidx}, {"lid", lid}, {"qpn", qpn}, {"psn", psn}, {"mtu", mtu}};
    }

} rdma_info_t;

}  // namespace slime
