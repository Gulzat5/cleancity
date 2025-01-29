import React from "react";
import { useSelector } from "react-redux";
import { Route, Routes } from "react-router-dom";

const USER_ROLE = {
  USER: "USER",
  VOLONTER: "VOLONTER",
};

export const MainRoutes = () => {
  const role = useSelector((state) => state.auch.user.role);
  const isAllowed = (roles) => {
    return roles.includes(role);
  };
  return (
    <Routes>
      <Route
        path="/user"
        element={
          <ProtectedRouted
            isAllowed={isAllowed([USER_ROLE.USER])}
            fallBackPatch="/"
            component={App}
          />
        }
      />
    </Routes>
  );
};
