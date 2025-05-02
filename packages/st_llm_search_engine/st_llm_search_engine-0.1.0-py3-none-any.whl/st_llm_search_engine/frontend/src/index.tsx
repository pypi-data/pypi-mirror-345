// frontend/src/index.tsx

import React from "react";
import ReactDOM from "react-dom";
import {
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib";
import {
  GoogleOAuthProvider,
  GoogleLogin,
  CredentialResponse,
} from "@react-oauth/google";

// 定義從 Python 端傳進來的 args 型別
interface Props {
  args: {
    clientId: string;
  };
}

const App: React.FC<Props> = ({ args }) => {
  // 從 props.args 拿到 clientId
  const clientId = args.clientId;

  // 成功取得 credential 時，透過 setComponentValue 回傳 token
  const onSuccess = (resp: CredentialResponse) => {
    if (resp.credential) {
      Streamlit.setComponentValue({ token: resp.credential });
    }
  };

  // 失敗時也回傳 error 欄位給 Python 端
  const onError = () => {
    Streamlit.setComponentValue({ error: "Google Login failed" });
  };

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <div style={{ textAlign: "center", marginTop: 30 }}>
        <GoogleLogin onSuccess={onSuccess} onError={onError} />
      </div>
    </GoogleOAuthProvider>
  );
};

// 用 withStreamlitConnection 包裝，會自動把 args 注入給 App
const WrappedApp = withStreamlitConnection(App);

ReactDOM.render(<WrappedApp />, document.getElementById("root"));
