<!-- 國曆排盤結果 區塊 -->
<div class="space-y-4 text-white">
  
  <h2 class="text-xl font-bold text-amber-400 tracking-wide">〔 國曆排盤結果 〕</h2>

  <!-- 三欄式結構 (手機單欄，電腦 lg 螢幕以上三欄) -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    
    <!-- 第一欄：國曆．核心指標 (🆕 新增的獨立格子) -->
    <div class="bg-[#182032] border border-amber-500/30 rounded-xl p-5 flex flex-col justify-between shadow-lg shadow-black/30">
      <h3 class="text-sm font-semibold text-slate-300 border-b border-slate-700/60 pb-3 mb-4">
        國曆．核心指標
      </h3>
      
      <div class="space-y-4 my-auto">
        <!-- 目標數 -->
        <div class="bg-[#101625] border border-slate-700/50 rounded-lg p-3 flex items-center justify-between">
          <span class="text-xs text-slate-400 font-medium">🎯 目標數</span>
          <span class="text-xl font-extrabold text-amber-400 tracking-wider">
            3 <span class="text-xs font-normal text-slate-300">號人</span>
          </span>
        </div>

        <!-- 格局數 -->
        <div class="bg-[#101625] border border-slate-700/50 rounded-lg p-3 flex items-center justify-between">
          <span class="text-xs text-slate-400 font-medium">🔢 格局數</span>
          <span class="text-xl font-extrabold text-amber-400 tracking-wider">30</span>
        </div>

        <!-- 命格屬性 -->
        <div class="bg-[#101625] border border-slate-700/50 rounded-lg p-3 flex items-center justify-between">
          <span class="text-xs text-slate-400 font-medium">☯️ 命格屬性</span>
          <div class="flex items-center gap-1.5">
            <span class="text-sm font-bold text-slate-100">比肩格</span>
            <span class="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded">未入格</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 第二欄：國曆．神煞排盤矩陣 -->
    <div class="bg-[#182032] border border-slate-700/60 rounded-xl p-5 shadow-lg shadow-black/30">
      <h3 class="text-sm font-semibold text-slate-300 border-b border-slate-700/60 pb-3 mb-4">
        國曆．神煞排盤矩陣
      </h3>
      
      <!-- 2x3 神煞矩陣 -->
      <div class="grid grid-cols-3 gap-2.5 my-auto">
        <!-- 第一排 -->
        <div class="bg-[#101625] border border-slate-600/60 rounded-lg h-20 flex items-center justify-center relative shadow-inner">
          <span class="text-base font-bold text-slate-100">正官</span>
          <span class="absolute top-1 right-1.5 text-[10px] text-amber-400 font-extrabold">2</span>
        </div>
        <div class="bg-[#101625] border border-slate-600/60 rounded-lg h-20 flex items-center justify-center">
          <span class="text-base font-bold text-slate-100">正印</span>
        </div>
        <div class="bg-[#101625] border-2 border-amber-400 rounded-lg h-20 flex items-center justify-center shadow-[0_0_10px_rgba(251,191,36,0.2)]">
          <span class="text-base font-bold text-amber-300">食神</span>
        </div>

        <!-- 第二排 -->
        <div class="bg-[#101625] border border-slate-600/60 rounded-lg h-20 flex items-center justify-center">
          <span class="text-base font-bold text-slate-100">七煞</span>
        </div>
        <div class="bg-[#101625] border border-slate-600/60 rounded-lg h-20 flex items-center justify-center">
          <span class="text-base font-bold text-slate-100">劫財</span>
        </div>
        <div class="bg-[#101625] border border-slate-600/60 rounded-lg h-20 flex items-center justify-center relative">
          <span class="text-base font-bold text-slate-100">劫財</span>
          <span class="absolute top-1 right-1.5 text-xs text-amber-400 font-bold">x</span>
        </div>
      </div>
    </div>

    <!-- 第三欄：國曆．格局能量排列 -->
    <div class="bg-[#182032] border border-slate-700/60 rounded-xl p-5 shadow-lg shadow-black/30">
      <h3 class="text-sm font-semibold text-slate-300 border-b border-slate-700/60 pb-3 mb-4">
        國曆．格局能量排列
      </h3>
      
      <div class="space-y-3 my-auto">
        <div class="flex items-center gap-2 text-base font-bold text-amber-400">
          <span>+</span> <span>食神</span>
        </div>
        <div class="flex items-center gap-2 text-base font-bold text-amber-400">
          <span>-</span> <span>劫財</span>
        </div>
        <div class="flex items-center gap-2 text-base font-bold text-amber-400">
          <span>+</span> <span>劫財x</span>
        </div>
        <div class="flex items-center gap-2 text-base font-bold text-amber-400">
          <span>-</span> <span>正印</span>
        </div>
      </div>
    </div>

  </div>
</div>
