#!/bin/bash
# ============================================================
# ZR-BOOTSTRAP 同源节点自启动引导 V1.0
# 用途: 写入crontab保活(worker掉线自动拉起) + 立即启动worker
# 位置: /mnt/workspace/zr_bootstrap.sh (持久层, 容器重建保留)
# 协议: NTFY-CONNECT-001 V1.4
# ============================================================
set -e
cd /mnt/workspace

# 1. 安装保活crontab (每2分钟检查, worker掉线自动拉起; 容器重建后需重跑本脚本)
cat > /tmp/zr_cron.txt << 'EOF'
*/2 * * * * pgrep -f "python3 zr_node_worker.py" >/dev/null || (cd /mnt/workspace && nohup python3 zr_node_worker.py >> worker_stdout.log 2>&1 &)
@reboot sleep 10 && bash /mnt/workspace/zr_bootstrap.sh
EOF
crontab /tmp/zr_cron.txt 2>/dev/null && echo "crontab: 已安装保活(2分钟) + @reboot自启"

# 2. 检查凭证目录 (持久层)
mkdir -p /mnt/workspace/.zr
chmod 700 /mnt/workspace/.zr
if [ -f /mnt/workspace/.zr/node_token.env ]; then
  echo "凭证: /mnt/workspace/.zr/node_token.env 已就位"
else
  echo "凭证: 未找到节点token, 请执行注入命令"
fi

# 3. 立即启动worker (若未运行)
if pgrep -f "python3 zr_node_worker.py" >/dev/null 2>&1; then
  echo "worker: 已在运行 (PID $(pgrep -f 'python3 zr_node_worker.py' | head -1))"
else
  nohup python3 zr_node_worker.py >> worker_stdout.log 2>&1 &
  sleep 2
  if pgrep -f "python3 zr_node_worker.py" >/dev/null 2>&1; then
    echo "worker: 已启动 (PID $(pgrep -f 'python3 zr_node_worker.py' | head -1))"
  else
    echo "worker: 启动失败, 检查 worker_stdout.log"
  fi
fi

echo "ZR-BOOTSTRAP-DONE"
